<script setup lang="ts">
import type { InterfaceCopy, Language } from './interface-copy'
import type { Study } from './study-api'

defineProps<{ study: Study; copy: InterfaceCopy; language: Language }>()

function yesNo(value: boolean | null, copy: InterfaceCopy) {
  if (value === null) return copy.missing
  return value ? copy.yes : copy.no
}

function sexText(value: string | null, copy: InterfaceCopy) {
  if (!value) return copy.missing
  const labels: Record<string, string> = {
    ALL: copy.sexAll,
    FEMALE: copy.sexFemale,
    MALE: copy.sexMale,
  }
  return labels[value] ?? value
}
</script>

<template>
  <details class="participation">
    <summary>{{ copy.participation }}</summary>
    <p>{{ copy.participationIntro }}</p>
    <dl class="participation-facts">
      <div>
        <dt>{{ copy.minAge }}</dt>
        <dd>{{ study.eligibility.minimum_age || copy.missing }}</dd>
      </div>
      <div>
        <dt>{{ copy.maxAge }}</dt>
        <dd>{{ study.eligibility.maximum_age || copy.missing }}</dd>
      </div>
      <div>
        <dt>{{ copy.sexEligibility }}</dt>
        <dd>{{ sexText(study.eligibility.sex, copy) }}</dd>
      </div>
      <div>
        <dt>{{ copy.healthyVolunteers }}</dt>
        <dd>{{ yesNo(study.eligibility.healthy_volunteers, copy) }}</dd>
      </div>
      <div>
        <dt>{{ copy.genderBased }}</dt>
        <dd>{{ yesNo(study.eligibility.gender_based, copy) }}</dd>
      </div>
      <div v-if="study.eligibility.gender_based || study.eligibility.gender_description">
        <dt>{{ copy.genderDescription }}</dt>
        <dd>{{ study.eligibility.gender_description || copy.missing }}</dd>
      </div>
    </dl>
    <h4>{{ copy.criteriaOriginal }}</h4>
    <p>{{ copy.criteriaNote }}</p>
    <p class="criteria-text" :lang="study.eligibility.criteria ? 'en' : language">
      {{ study.eligibility.criteria || copy.criteriaMissing }}
    </p>
    <a :href="study.source_url" target="_blank" rel="noopener noreferrer"
      >{{ copy.criteriaSource }} ↗</a
    >
  </details>
</template>
