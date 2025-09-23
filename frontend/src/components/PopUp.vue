<script setup lang="ts">
import {ref} from "vue";

const isOpen = ref(true)

const toggle = () => {
  isOpen.value = !isOpen.value;
}

</script>

<template>
  <div class="dark" @click="toggle()" v-if="isOpen"></div>
  <div class="popup" :class="{ 'go-right': !isOpen}" >
    <slot></slot>
  </div>
</template>

<style scoped>
.popup {
  height: 100vh;
  width: 50vw;
  position: fixed;
  top: 0;
  right: 0;
  background-color: aliceblue;
}

.dark{
  position: fixed;
  height: 100vh;
  width: 50vw;
  top: 0;
  left: 0;
  background-color: black;
  opacity: 0.5;
}
.go-right {
  animation: animation 1s;
  animation-fill-mode: forwards;
}

@keyframes animation {
  from {
    right: 0;
  }
  to{
    transform: translateX(100%);
  }
}
</style>
