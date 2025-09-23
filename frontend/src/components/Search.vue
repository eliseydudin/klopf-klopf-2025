<script setup lang="ts">
import { ref } from 'vue';
import { useFetch } from '@vueuse/core';

const message = ref("")
const error = defineModel<string | null>({ required: true })

const onClick = async () => {
  const fetchResult = await useFetch("https://httpbin.org/get");

  if (fetchResult.error) {
    error.value = fetchResult.error.value;
  } else {
    error.value = null;
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
