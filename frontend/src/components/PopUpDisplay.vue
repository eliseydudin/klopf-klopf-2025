<script setup lang="ts">
import type { StationStats } from "@/types";
import { ShieldAlert } from "lucide-vue-next";

const { data } = defineProps<{ data: StationStats }>();
console.log(data);

const getColorFromType = (type: number) => {
  if (type === 0) {
    return "orange";
  } else {
    return "red"
  }
}

const dateFromTime = (time: number) => {
  const date = new Date(time);
  const hours = date.getHours();
  const minutes = date.getMinutes();
  return `${hours}:${minutes}`
}

const getText = (type: number) => {
  if (type === 0) {
    return "Падение с эскалатора"
  } else if (type === 1) {
    return "Драка на эскалаторе"
  } else {
    return "unknown"
  }
}
</script>

<template>
  <div class="container_station">
    <h2 class="station_title">Станция: {{ data.station }}</h2>
    <h3>Ветка: {{ data.branch }} </h3>
    <p>Инцидентов за сегодняшний день: {{ data.today_events_amount }}</p>
    <p>Последние происшествия:</p>
    <div class="list_incidents">
      <div class="incidents" v-for='item in data.latest_events'>
        <ShieldAlert :color="getColorFromType(item.type)"></ShieldAlert>
        <p>{{ getText(item.type) }}</p>
        <p style="color:grey">{{ dateFromTime(item.timestamp) }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container_station {
  margin: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.station_title {
  justify-content: center;
  display: flex;
}

.incidents {
  display: flex;
  gap: 6px;
  align-items: center;
}

.list_incidents {
  display: flex;
  gap: 10px;
  flex-direction: column;
  margin-left: 10px;
  border: black solid 1px;
  border-radius: 10px;
  padding: 10px;
}
</style>
