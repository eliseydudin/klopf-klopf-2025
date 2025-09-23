<script setup lang="ts">
import { ref } from 'vue';
import { useFetch } from '@vueuse/core';
import type { StationStats } from '@/types';

const message = ref("")
const error = defineModel<string | null>({ required: true })
const fetchResult = defineModel<null | StationStats>("result", { required: true })

const onClick = async () => {
  const { data, error: fetchError } = await useFetch(`http://0.0.0.0:8000/incident/station/statistics/${message.value}`).json();
  console.log(`data: ${data.value}, error: ${error.value}`)

  if (fetchError.value) {
    error.value = "Произошла ошибка! Проверьте написание названия станции";
  } else {
    error.value = null;
    fetchResult.value = data.value as StationStats
  }
}

</script>

<template>
  <div class="container_search">
    <input placeholder="Первомайская" class="text_search" type="text" v-model="message" />
    <button @click="onClick()" class="button_search">Найти</button>
  </div>
</template>

<style scoped>
.container_search {
  margin: 30px;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.text_search {
  width: 200px;
  border: none;
  border-bottom: 1px solid black;
  font-size: 16px;
}

.text_search:active,
.text_search:focus {
  outline: none;
}

.button_search {
  width: 90px;
  font-size: 16px;
  border: none;
  border-radius: 10px;
  color: white;
  transition: .2s linear;
  background-color: #0B63F6;
  padding: 10px;
}

.button_search:hover {
  box-shadow: 0 0 0 2px white, 0 0 0 4px #3C82F8;
}

.button_search:active {
  background-color: #0A4BC4;
}
</style>
