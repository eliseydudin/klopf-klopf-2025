<script setup lang="ts">
import { onMounted, onUnmounted, useTemplateRef } from 'vue';
import App from './app'


let app: App | null;
const elem = useTemplateRef("current");

onMounted(() => {
  if (elem.value === null) {
    return;
  }

  app = new App(elem.value);
  console.log("мапа инициализирована йипи")
})

onUnmounted(() => {
  if (app === null) {
    console.log("мапы нет пошёл нахуй")
    return;
  }

  app.destroy();
})

</script>

<template>
  <div ref="current"></div>
</template>

<style lang="css">
.moscow_metro_map {
  cursor: -webkit-grab;
  cursor: grab;
  transition: opacity 0.5s;
  font-size: 0.7em;
}

.moscow_metro_map.drag {
  cursor: -webkit-grabbing;
  cursor: grabbing;
}

.moscow_metro_map__station {
  position: relative;
  display: block;
  cursor: pointer;
}

.moscow_metro_map__substrate {
  fill: rgba(255, 255, 255, 0.6);
}

.moscow_metro_map__area {
  fill: rgba(255, 255, 255, 0);
}

.moscow_metro_map__station text {
  color: #333333;
}

.selected .moscow_metro_map__substrate {
  fill: rgba(255, 205, 30, 0.5)
}

.moscow_metro_map__check {
  opacity: 0;
  transition: 0.2s;
}

.moscow_metro_map__check.selected {
  opacity: 1;
}
</style>
