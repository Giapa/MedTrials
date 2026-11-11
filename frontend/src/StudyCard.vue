<script setup lang="ts">
import type { InterfaceCopy, Language } from './interface-copy'
import type { Study } from './study-api'

defineProps<{ study: Study; copy: InterfaceCopy; language: Language }>()

function statusText(status: string | null | undefined, copy: InterfaceCopy) {
  if (!status) return copy.missing
  const labels: Record<string, string> = {
    RECRUITING: copy.recruiting,
    NOT_YET_RECRUITING: copy.notYetRecruiting,
    ACTIVE_NOT_RECRUITING: copy.activeNotRecruiting,
    COMPLETED: copy.completed,
    ENROLLING_BY_INVITATION: copy.invitation,
    SUSPENDED: copy.suspended,
    TERMINATED: copy.terminated,
    WITHDRAWN: copy.withdrawn,
    UNKNOWN: copy.unknown,
  }
  return labels[status] ?? status
}
</script>

<template>
  <article class="study-card">
    <div class="card-heading">
      <div>
        <span class="identifier">{{ study.id }}</span>
        <h3 lang="en">{{ study.title }}</h3>
      </div>
      <span class="status">{{ statusText(study.status, copy) }}</span>
    </div>
    <p class="original">{{ copy.original }}</p>
    <dl class="facts">
      <div>
        <dt>{{ copy.status }}</dt>
        <dd>
          {{ statusText(study.status, copy) }}
        </dd>
      </div>
      <div>
        <dt>{{ copy.updated }}</dt>
        <dd>{{ study.last_updated ?? copy.missing }}</dd>
      </div>
    </dl>
    <div class="detail">
      <h4>{{ copy.about }}</h4>
      <p :lang="study.summary ? 'en' : language">{{ study.summary ?? copy.missing }}</p>
    </div>
    <div class="detail">
      <h4>{{ copy.locations }}</h4>
      <ul v-if="study.locations.length">
        <li v-for="(location, index) in study.locations" :key="index">
          {{ location.facility ?? copy.missing
          }}<template v-if="location.city"> · {{ location.city }}</template>
          <span v-if="'status' in location">
            — {{ copy.siteStatus }}: {{ statusText(location.status, copy) }}</span
          >
        </li>
      </ul>
      <p v-else>{{ copy.noLocations }}</p>
    </div>
    <div class="card-footer">
      <a :href="study.source_url" target="_blank" rel="noopener noreferrer">{{ copy.source }} ↗</a>
      <p>{{ copy.caveat }}</p>
    </div>
  </article>
</template>
