<script setup lang="ts">
import type { InterfaceCopy, Language } from './interface-copy'
import type { Study } from './study-api'

defineProps<{ study: Study; copy: InterfaceCopy; language: Language }>()
</script>

<template>
  <article class="study-card">
    <div class="card-heading">
      <div>
        <span class="identifier">{{ study.id }}</span>
        <h3 lang="en">{{ study.title }}</h3>
      </div>
      <span class="status">{{
        study.status === 'COMPLETED' ? copy.completed : (study.status ?? copy.missing)
      }}</span>
    </div>
    <p class="original">{{ copy.original }}</p>
    <dl class="facts">
      <div>
        <dt>{{ copy.status }}</dt>
        <dd>
          {{ study.status === 'COMPLETED' ? copy.completed : (study.status ?? copy.missing) }}
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
