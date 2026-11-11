<script setup lang="ts">
import { ref } from 'vue'
import StudyCard from './StudyCard.vue'
import type { InterfaceCopy, Language } from './interface-copy'
import { searchStudies, type SearchResults } from './study-api'

defineProps<{ copy: InterfaceCopy; language: Language }>()

const condition = ref('')
const openStudiesOnly = ref(false)
const state = ref<
  | { kind: 'idle' }
  | { kind: 'loading' }
  | { kind: 'error' }
  | { kind: 'results'; results: SearchResults }
>({ kind: 'idle' })

async function search() {
  const term = condition.value.trim()
  if (!term || state.value.kind === 'loading') return
  state.value = { kind: 'loading' }
  try {
    state.value = { kind: 'results', results: await searchStudies(term, openStudiesOnly.value) }
  } catch {
    state.value = { kind: 'error' }
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
        />
        <button type="submit" :disabled="state.kind === 'loading' || !condition.trim()">
          {{ state.kind === 'loading' ? copy.searching : copy.searchButton }}
        </button>
      </div>
      <label class="filter-option">
        <input v-model="openStudiesOnly" name="openStudiesOnly" type="checkbox" />
        {{ copy.openOnly }}
      </label>
      <p class="filter-help">{{ copy.filterHelp }}</p>
      <p class="search-privacy">{{ copy.privacy }}</p>
    </form>
    <div aria-live="polite">
      <p v-if="state.kind === 'error'" class="message" role="alert">{{ copy.searchError }}</p>
      <div v-else-if="state.kind === 'results'" class="search-results">
        <h3>{{ copy.results }}</h3>
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
      </div>
    </div>
  </section>
</template>
