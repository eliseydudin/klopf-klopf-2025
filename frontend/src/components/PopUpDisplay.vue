<script setup lang="ts">
import {ShieldAlert} from "lucide-vue-next";

const events = [
  {
    id: 1, timestamp: 123123123, type: 0
  },
  {
    id: 2, timestamp: 123123124, type: 1
  }
];

const getColorFromType = (type: number) => {
  if (type === 0) {
    return "orange";
  } else if (type === 1) {
    return "red"
  }
}
const getText = (type: number) => {
  if (type === 0) {
    return "Падение с эскалатора"
  } else if (type === 1) {
    return "Драка на эскалаторе"
  }
}
</script>

<template>
  <div class="container_station">
    <h2 class="station_title">Станция: Первомайская</h2>
    <h3>Ветка: Арбатско-покровская</h3>
    <p>Инцидентов за сегодняшний день: 2</p>
    <p>Последние происшествия:</p>
    <div class="list_incidents">
      <div class="incidents" v-for="item in events">
        <ShieldAlert :color="getColorFromType(item.type)"></ShieldAlert>
        <p>{{ getText(item.type) }}</p>
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
  gap: 4px;
  align-items: center;
}

.list_incidents{
  display: flex;
  gap: 10px;
  flex-direction: column;
  margin-left: 10px;
  border: black solid 1px;
  border-radius: 10px;
  padding: 10px;
}
</style>
