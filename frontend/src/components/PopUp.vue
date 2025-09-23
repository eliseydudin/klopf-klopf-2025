<script setup lang="ts">
import type { StationStats } from "@/types";
import { computed } from "vue";
import PopUpDisplay from "@/components/PopUpDisplay.vue";

const data = defineModel<null | StationStats>({ required: true })
const isOpen = computed({
  get: () => /*data.value !== null*/true, set: (value) => {
    if (!value) data.value = null;
  }
});

const toggle = () => {
  if (isOpen.value) {
    isOpen.value = false;
  }
}

</script>

<template>
  <div class="dark" @click="toggle()" :class="{ 'go': !isOpen }"></div>
  <div class="popup" :class="{ 'go-right': !isOpen }">
    <PopUpDisplay></PopUpDisplay>
  </div>
</template>

<style scoped>
.popup {
  height: 100vh;
  width: 35vw;
  position: fixed;
  top: 0;
  right: 0;
  background-color: #FAFFFF;
}

.dark {
  position: fixed;
  height: 100vh;
  width: 100vw;
  top: 0;
  left: 0;
  background-color: black;
  opacity: 0.5;
}

.go {
  animation: go 1s;
  animation-fill-mode: forwards;

}

@keyframes go {
  0% {
    opacity: 0.5;
  }

  99.99% {
    opacity: 0;
  }

  100% {
    width: 0;
  }
}

.go-right {
  animation: animation 1s;
  animation-fill-mode: forwards;
}

@keyframes animation {
  from {
    right: 0;
  }

  to {
    transform: translateX(100%);
  }
}
</style>
