<script setup lang="ts">
import MetroMap from './components/metro_map/MetroMap.vue';
import PopUp from "@/components/PopUp.vue";
import Search from "@/components/Search.vue";
import Message from "@/components/Message.vue";
import { ref } from 'vue';

const error = ref<string | null>(null);

</script>

<template>
  <div class="container">
    <header>
      <div class="icon_container">
        <img class="icon_metro" src="/img_metro.png" alt="Иконка метро">
        <div class="icon_metro_text">
          <p>Московский</p>
          <p>метрополитен</p>
        </div>
      </div>
    </header>
    <h1 class="title">Система мониторинга и выявления инцидентов на эскалаторах Московского
      Метрополитена</h1>
    <PopUp></PopUp>
    <Search v-model="error"></Search>
    <Message v-model="error"></Message>
  </div>

  <MetroMap></MetroMap>
</template>

<style scoped>
.title {
  font-size: 20px;
  margin-top: 20px;
}

.icon_container {
  display: flex;
  font-size: 12px;
  color: #c83533;
  font-weight: bold;
}

.icon_metro {
  width: 40px;
  height: 40px;
}

.icon_metro_text {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card {
  width: 1000px;
}
</style>

<style>
* {
  font-family: "Mulish", serif;
  padding: 0;
  margin: 0;
}

.container {
  width: 1200px;
  margin: 0 auto;
  padding: 30px 10px;
}
</style>
