<script setup lang="ts">
import { computed, ref } from 'vue'
import StudyCard from './StudyCard.vue'
import { findGreekConditionTerm, hasGreekText } from './greek-condition-terms'
import type { InterfaceCopy, Language } from './interface-copy'
import { RegistryBusyError, searchStudies, type SearchResults } from './study-api'

defineProps<{ copy: InterfaceCopy; language: Language }>()

const condition = ref('')
const containsGreek = computed(() => hasGreekText(condition.value))
const suggestion = computed(() => findGreekConditionTerm(condition.value))
const chosenTerm = ref<{ greek: string; sourceUrl: string } | null>(null)
const openStudiesOnly = ref(false)
const state = ref<
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'error'; busy: boolean }
  | {
      kind: 'results'
      results: SearchResults
      term: string
      openOnly: boolean
      loadingMore: boolean
      moreError: 'busy' | 'generic' | null
    }
>({ kind: 'idle' })
let searchVersion = 0

function useSuggestion() {
  if (!suggestion.value) return
  chosenTerm.value = { greek: condition.value.trim(), sourceUrl: suggestion.value.sourceUrl }
  condition.value = suggestion.value.english
}

async function search() {
  const term = condition.value.trim()
  if (!term || containsGreek.value || state.value.kind === 'loading') return
  const openOnly = openStudiesOnly.value
  const version = ++searchVersion
  state.value = { kind: 'loading' }
  try {
    const results = await searchStudies(term, openOnly)
    if (version === searchVersion)
      state.value = {
        kind: 'results',
        results,
        term,
        openOnly,
        loadingMore: false,
        moreError: null,
      }
  } catch (reason) {
    if (version === searchVersion)
      state.value = { kind: 'error', busy: reason instanceof RegistryBusyError }
  }
}

async function loadMore() {
  const current = state.value
  if (current.kind !== 'results' || current.loadingMore || !current.results.next_page_token) return
  const token = current.results.next_page_token
  const version = searchVersion
  state.value = { ...current, loadingMore: true, moreError: null }
  try {
    const next = await searchStudies(current.term, current.openOnly, token)
    if (next.next_page_token === token) throw new Error('Repeated registry page token')
    if (version !== searchVersion) return
    const ids = new Set(current.results.studies.map((study) => study.id))
    const studies = [...current.results.studies]
    for (const study of next.studies) {
      if (!ids.has(study.id)) {
        ids.add(study.id)
        studies.push(study)
      }
    }
    state.value = {
      ...current,
      results: { ...next, studies },
      loadingMore: false,
      moreError: null,
    }
  } catch (reason) {
    if (version === searchVersion)
      state.value = {
        ...current,
        loadingMore: false,
        moreError: reason instanceof RegistryBusyError ? 'busy' : 'generic',
      }
  }
}
</script>

<template>
  <section class="search-section">
    <h2>{{ copy.searchTitle }}</h2>
    <p>{{ copy.searchIntro }}</p>
    <form class="search-form" @submit.prevent="search">
      <label for="condition">{{ copy.condition }}</label>
      <div class="search-controls">
        <input
          id="condition"
          v-model="condition"
          name="condition"
          type="text"
          maxlength="120"
          required
          autocomplete="off"
          @input="chosenTerm = null"
        />
        <button
          type="submit"
          :disabled="state.kind === 'loading' || !condition.trim() || containsGreek"
        >
          {{ state.kind === 'loading' ? copy.searching : copy.searchButton }}
        </button>
      </div>
      <div v-if="containsGreek" aria-live="polite" class="greek-help">
        <div v-if="suggestion" class="term-suggestion">
          <p>
            {{ copy.suggestedTerm }} <strong lang="en">{{ suggestion.english }}</strong>
          </p>
          <p>{{ copy.suggestionLimit }}</p>
          <a :href="suggestion.sourceUrl" target="_blank" rel="noopener noreferrer">{{
            copy.termSource
          }}</a>
          <button class="retry" name="use-suggested-term" type="button" @click="useSuggestion">
            {{ copy.useTerm }}
          </button>
        </div>
        <p v-else>{{ copy.greekUnsupported }}</p>
        <p>{{ copy.greekHelp }}</p>
      </div>
      <p v-if="chosenTerm" class="chosen-term">
        {{ copy.chosenFrom }} <strong>{{ chosenTerm.greek }}</strong> ·
        <a :href="chosenTerm.sourceUrl" target="_blank" rel="noopener noreferrer">{{
          copy.termSource
        }}</a>
      </p>
      <p class="registry-alternative">
        {{ copy.mapIntro }}
        <a
          href="https://trialmap.ema.europa.eu/?language=el"
          target="_blank"
          rel="noopener noreferrer"
          >{{ copy.mapLink }}</a
        >
        {{ copy.mapPrivacy }}
      </p>
      <label class="filter-option">
        <input v-model="openStudiesOnly" name="openStudiesOnly" type="checkbox" />
        {{ copy.openOnly }}
      </label>
      <p class="filter-help">{{ copy.filterHelp }}</p>
      <p class="search-privacy">{{ copy.privacy }}</p>
    </form>
    <div aria-live="polite">
      <p v-if="state.kind === 'error'" class="message" role="alert">
        {{ state.busy ? copy.registryBusy : copy.searchError }}
      </p>
      <div v-else-if="state.kind === 'results'" class="search-results">
        <h3>{{ copy.results }}</h3>
        <p>
          {{ copy.resultsFor }}: <strong>{{ state.term }}</strong
          ><template v-if="state.openOnly"> · {{ copy.resultsFiltered }}</template>
        </p>
        <p>{{ copy.resultsNote }}</p>
        <p v-if="!state.results.studies.length">{{ copy.empty }}</p>
        <p v-if="state.results.more_results">{{ copy.moreResults }}</p>
        <StudyCard
          v-for="study in state.results.studies"
          :key="study.id"
          :study="study"
          :copy="copy"
          :language="language"
        />
        <p v-if="state.moreError" role="alert">
          {{ state.moreError === 'busy' ? copy.moreBusy : copy.moreError }}
        </p>
        <button
          v-if="state.results.more_results"
          class="retry"
          name="load-more"
          type="button"
          :disabled="state.loadingMore"
          @click="loadMore"
        >
          {{ state.loadingMore ? copy.loadingMore : copy.loadMore }}
        </button>
      </div>
    </div>
  </section>
</template>
