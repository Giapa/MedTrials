<script setup lang="ts">
import { computed, ref } from 'vue'
import { findGreekConditionTerm, hasGreekText } from './greek-condition-terms'
import { searchEuropeanStudies, type EuropeanSearchResults } from './eu-study-api'
import type { InterfaceCopy } from './interface-copy'
import { RegistryBusyError } from './study-api'

defineProps<{ copy: InterfaceCopy }>()
const emit = defineEmits<{ select: [id: string] }>()
const condition = ref('')
const containsGreek = computed(() => hasGreekText(condition.value))
const suggestion = computed(() => findGreekConditionTerm(condition.value))
const chosenTerm = ref<{ greek: string; sourceUrl: string } | null>(null)
const state = ref<
  | { kind: 'idle' | 'loading' }
  | { kind: 'error'; busy: boolean }
  | {
      kind: 'results'
      term: string
      results: EuropeanSearchResults
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
  const version = ++searchVersion
  state.value = { kind: 'loading' }
  try {
    const results = await searchEuropeanStudies(term, 1)
    if (version === searchVersion)
      state.value = { kind: 'results', term, results, loadingMore: false, moreError: null }
  } catch (reason) {
    if (version === searchVersion)
      state.value = { kind: 'error', busy: reason instanceof RegistryBusyError }
  }
}

async function loadMore() {
  const current = state.value
  if (current.kind !== 'results' || current.loadingMore || !current.results.more_results) return
  const version = searchVersion
  state.value = { ...current, loadingMore: true, moreError: null }
  try {
    const next = await searchEuropeanStudies(current.term, current.results.page + 1)
    if (version !== searchVersion) return
    const ids = new Set(current.results.studies.map((study) => study.id))
    const studies = [...current.results.studies]
    for (const study of next.studies) {
      if (!ids.has(study.id)) {
        ids.add(study.id)
        studies.push(study)
      }
    }
    state.value = { ...current, results: { ...next, studies }, loadingMore: false, moreError: null }
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
  <section class="eu-search">
    <h3>{{ copy.euSearchTitle }}</h3>
    <p>{{ copy.euSearchIntro }}</p>
    <form class="search-form" @submit.prevent="search">
      <label for="eu-condition">{{ copy.condition }}</label>
      <div class="search-controls">
        <input
          id="eu-condition"
          v-model="condition"
          name="eu-condition"
          type="text"
          maxlength="120"
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
      <div v-if="containsGreek" class="greek-help" aria-live="polite">
        <div v-if="suggestion" class="term-suggestion">
          <p>
            {{ copy.suggestedTerm }} <strong lang="en">{{ suggestion.english }}</strong>
          </p>
          <p>{{ copy.suggestionLimit }}</p>
          <a :href="suggestion.sourceUrl" target="_blank" rel="noopener noreferrer">{{
            copy.termSource
          }}</a>
          <button class="retry" name="eu-use-term" type="button" @click="useSuggestion">
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
      <p class="search-privacy">{{ copy.euSearchPrivacy }}</p>
    </form>
    <div aria-live="polite">
      <p v-if="state.kind === 'error'" class="message" role="alert">
        {{ state.busy ? copy.euBusy : copy.euError }}
      </p>
      <div v-else-if="state.kind === 'results'" class="eu-search-results">
        <p>
          {{ copy.resultsFor }}: <strong>{{ state.term }}</strong> · {{ copy.euTotal }}:
          {{ state.results.total }}
        </p>
        <p>{{ copy.euSearchNote }}</p>
        <p v-if="!state.results.studies.length">{{ copy.euEmpty }}</p>
        <article v-for="study in state.results.studies" :key="study.id" class="study-card">
          <span class="identifier">{{ study.id }}</span>
          <h4 lang="en">{{ study.title }}</h4>
          <p v-if="study.condition" lang="en">{{ study.condition }}</p>
          <a :href="study.source_url" target="_blank" rel="noopener noreferrer"
            >{{ copy.euSource }} ↗</a
          >
          <button
            class="retry eu-select"
            name="eu-select"
            type="button"
            @click="emit('select', study.id)"
          >
            {{ copy.euViewCriteria }}
          </button>
        </article>
        <p v-if="state.moreError" role="alert">
          {{ state.moreError === 'busy' ? copy.euMoreBusy : copy.moreError }}
        </p>
        <button
          v-if="state.results.more_results"
          class="retry"
          name="eu-load-more"
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
