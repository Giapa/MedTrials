<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import StudyCard from './StudyCard.vue'
import StudySearch from './StudySearch.vue'
import { interfaceCopy, type Language } from './interface-copy'
import { fetchExampleStudy, RegistryBusyError, type Study } from './study-api'

const language = ref<Language>('el')
const study = ref<Study | null>(null)
const loading = ref(true)
const error = ref<'busy' | 'generic' | null>(null)
const copy = computed(() => interfaceCopy[language.value])

async function loadStudy() {
  loading.value = true
  error.value = null
  try {
    study.value = await fetchExampleStudy()
  } catch (reason) {
    study.value = null
    error.value = reason instanceof RegistryBusyError ? 'busy' : 'generic'
  } finally {
    loading.value = false
  }
}

watch(language, (value) => {
  document.documentElement.lang = value
})
onMounted(loadStudy)
</script>

<template>
  <a class="skip" href="#main">{{ copy.skip }}</a>
  <header class="topbar">
    <div class="wrap topbar-inner">
      <span class="brand"><span aria-hidden="true" class="brand-mark">✳</span> MedTrials</span>
      <div class="language" aria-label="Language">
        <button :aria-pressed="language === 'el'" @click="language = 'el'">ΕΛ</button
        ><button :aria-pressed="language === 'en'" @click="language = 'en'">EN</button>
      </div>
    </div>
  </header>
  <main id="main" class="wrap">
    <section class="intro">
      <p class="eyebrow">{{ copy.tag }}</p>
      <h1>{{ copy.title }}</h1>
      <p class="lead">{{ copy.intro }}</p>
      <div class="notice">
        <span aria-hidden="true">i</span>
        <p>{{ copy.notice }}</p>
      </div>
    </section>
    <StudySearch :copy="copy" :language="language" />
    <section class="study-section" aria-live="polite">
      <div class="section-heading">
        <div>
          <p class="eyebrow">{{ copy.eyebrow }}</p>
          <h2>ClinicalTrials.gov</h2>
        </div>
        <p>{{ copy.example }}</p>
      </div>
      <div v-if="loading" class="message">{{ copy.loading }}</div>
      <div v-else-if="error" class="message" role="alert">
        <p>{{ error === 'busy' ? copy.registryBusy : copy.error }}</p>
        <button class="retry" @click="loadStudy">{{ copy.retry }}</button>
      </div>
      <StudyCard v-else-if="study" :study="study" :copy="copy" :language="language" />
      <p class="scope">{{ copy.scope }}</p>
    </section>
  </main>
</template>
