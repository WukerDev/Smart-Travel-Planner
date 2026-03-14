<template>
  <v-container class="mt-5">
    <v-card class="pa-5 mx-auto" max-width="400" elevation="4">
      <v-card-title>Moduł Pogody</v-card-title>
      <v-card-text>
        <p>Miasto: <strong>{{ weatherStore.city }}</strong></p>
        <p>Temperatura: <strong>{{ weatherStore.temperature }}°C</strong></p>
      </v-card-text>
      <v-card-actions>
        <v-btn color="primary" @click="changeCity">Zmień na Paryż</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { useWeatherStore } from './store.js'

// Inicjalizacja store'a
const weatherStore = useWeatherStore()

// Funkcja testująca zmianę stanu
const changeCity = () => {
  weatherStore.setCity('Paryż')
  weatherStore.temperature = 18
}
</script>