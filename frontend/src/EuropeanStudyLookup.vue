<script setup lang="ts">
import { ref } from 'vue'
import EuropeanStudySearch from './EuropeanStudySearch.vue'
import {
  EuropeanStudyNotFoundError,
  fetchEuropeanStudy,
  isEuropeanTrialNumber,
  type EuropeanStudy,
} from './eu-study-api'
import type { InterfaceCopy, Language } from './interface-copy'
import { RegistryBusyError } from './study-api'

defineProps<{ copy: InterfaceCopy; language: Language }>()
const trialId = ref('')
const lookupHeading = ref<HTMLHeadingElement | null>(null)
const state = ref<
  | { kind: 'idle' | 'loading' }
  | { kind: 'error'; reason: 'invalid' | 'not-found' | 'busy' | 'unavailable' }
  | { kind: 'result'; study: EuropeanStudy }
>({ kind: 'idle' })
let lookupVersion = 0

function selectTrial(id: string) {
  trialId.value = id
  void lookup()
  lookupHeading.value?.focus()
}

async function lookup() {
  const id = trialId.value.trim()
  const version = ++lookupVersion
  if (!isEuropeanTrialNumber(id)) {
    state.value = { kind: 'error', reason: 'invalid' }
    return
  }
  state.value = { kind: 'loading' }
  try {
    const study = await fetchEuropeanStudy(id)
    if (version === lookupVersion) state.value = { kind: 'result', study }
  } catch (reason) {
    if (version === lookupVersion)
      state.value = {
        kind: 'error',
        reason:
          reason instanceof EuropeanStudyNotFoundError
            ? 'not-found'
            : reason instanceof RegistryBusyError
              ? 'busy'
              : 'unavailable',
      }
  }
}
</script>

<template>
  <section class="search-section eu-section">
    <h2>{{ copy.euTitle }}</h2>
    <p>{{ copy.euIntro }}</p>
    <EuropeanStudySearch :copy="copy" @select="selectTrial" />
    <h3 ref="lookupHeading" class="eu-lookup-heading" tabindex="-1">{{ copy.euLookupTitle }}</h3>
    <form class="search-form eu-lookup-form" @submit.prevent="lookup">
      <label for="eu-trial-id">{{ copy.euNumber }}</label>
      <div class="search-controls">
        <input
          id="eu-trial-id"
          v-model="trialId"
          name="eu-trial-id"
          type="text"
          maxlength="18"
          autocomplete="off"
          :placeholder="copy.euExample"
        />
        <button type="submit" :disabled="state.kind === 'loading'">
          {{ state.kind === 'loading' ? copy.searching : copy.euButton }}
        </button>
      </div>
      <p class="search-privacy">{{ copy.euHelp }}</p>
    </form>
    <div aria-live="polite">
      <p v-if="state.kind === 'loading'">{{ copy.searching }}</p>
      <p v-else-if="state.kind === 'error'" class="message" role="alert">
        {{
          state.reason === 'invalid'
            ? copy.euInvalid
            : state.reason === 'not-found'
              ? copy.euNotFound
              : state.reason === 'busy'
                ? copy.euBusy
                : copy.euError
        }}
      </p>
      <article v-else-if="state.kind === 'result'" class="study-card eu-result">
        <span class="identifier">{{ state.study.id }}</span>
        <h3 :lang="language === 'el' && state.study.title.greek ? 'el' : 'en'">
          {{
            language === 'el'
              ? state.study.title.greek || state.study.title.english
              : state.study.title.english
          }}
        </h3>
        <p v-if="language === 'el' && !state.study.title.greek">{{ copy.euGreekMissing }}</p>
        <p>{{ copy.euCountry }}</p>
        <div class="detail eu-objective">
          <h4>{{ copy.euObjective }}</h4>
          <p>{{ copy.euObjectiveIntro }}</p>
          <template v-if="state.study.objective">
            <p
              v-if="language === 'el'"
              class="objective-text"
              :lang="state.study.objective.greek ? 'el' : 'en'"
            >
              {{ state.study.objective.greek || state.study.objective.english }}
            </p>
            <p v-else class="objective-text" :lang="state.study.objective.english ? 'en' : 'el'">
              {{ state.study.objective.english || state.study.objective.greek }}
            </p>
            <p v-if="language === 'el' && !state.study.objective.greek">
              {{ copy.euGreekMissing }}
            </p>
            <p v-if="language === 'en' && !state.study.objective.english">
              {{ copy.euEnglishMissing }}
            </p>
          </template>
          <p v-else>{{ copy.euObjectiveMissing }}</p>
          <a :href="state.study.source_url" target="_blank" rel="noopener noreferrer"
            >{{ copy.euObjectiveSource }} ↗</a
          >
        </div>
        <p>{{ copy.euCriteriaNote }}</p>
        <div
          v-for="group in [
            { name: copy.euInclusion, items: state.study.inclusion },
            { name: copy.euExclusion, items: state.study.exclusion },
          ]"
          :key="group.name"
          class="detail"
        >
          <h4>{{ group.name }}</h4>
          <ul v-if="group.items.length">
            <li v-for="(item, index) in group.items" :key="index">
              <span :lang="language === 'el' && item.greek ? 'el' : 'en'">{{
                language === 'el' ? item.greek || item.english : item.english
              }}</span>
              <span v-if="language === 'el' && !item.greek"> — {{ copy.euGreekMissing }}</span>
            </li>
          </ul>
          <p v-else>{{ copy.euCriteriaMissing }}</p>
        </div>
        <div class="card-footer">
          <a :href="state.study.source_url" target="_blank" rel="noopener noreferrer"
            >{{ copy.euSource }} ↗</a
          >
          <p>{{ copy.caveat }}</p>
        </div>
      </article>
    </div>
  </section>
</template>
