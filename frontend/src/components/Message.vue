<script setup lang="ts">
import {CircleX} from "lucide-vue-next";
</script>

<template>
  <div class="message">
    <CircleX color="red" :size="22" />
    <p class="text_message">Нет такой станции</p>
  </div>
</template>

<style scoped>
.message{
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
}
.text_message{
  font-size: 18px;
  background-color: white;
  color: red;
}
</style>
