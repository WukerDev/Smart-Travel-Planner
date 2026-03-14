<template>
  <v-container class="text-center mt-10">

    <div class="text-left mb-4">
      <v-btn variant="text" to="/" prepend-icon="mdi-arrow-left">
        Wróć do menu
      </v-btn>
    </div>

    <v-card class="pa-5 mx-auto" max-width="500" elevation="3">
      <h2 class="text-h5 mb-4">Sprawdź warunki na wyjazd</h2>

      <v-text-field
        v-model="cityInput"
        label="Wpisz nazwę miasta"
        variant="outlined"
        @keyup.enter="handleSearch"
      ></v-text-field>

      <v-btn
        color="primary"
        size="large"
        :loading="weatherStore.isLoading"
        @click="handleSearch"
      >
        Szukaj
      </v-btn>

      <v-alert v-if="weatherStore.error" type="error" class="mt-4" variant="tonal">
        {{ weatherStore.error }}
      </v-alert>

      <v-card v-if="weatherStore.data" color="blue-grey-lighten-5" class="mt-6 pa-4 text-left" elevation="1">
        <v-card-title class="text-h5 text-primary">
          {{ weatherStore.data.city }}
        </v-card-title>
        <v-card-text class="text-body-1">
          <v-row>
            <v-col cols="6">🌡️ Temperatura:</v-col>
            <v-col cols="6"><strong>{{ weatherStore.data.temperature }} °C</strong></v-col>

            <v-col cols="6">☁️ Opis:</v-col>
            <v-col cols="6"><strong>{{ weatherStore.data.description }}</strong></v-col>

            <v-col cols="6">💧 Wilgotność:</v-col>
            <v-col cols="6"><strong>{{ weatherStore.data.humidity }} %</strong></v-col>

            <v-col cols="6">💨 Wiatr:</v-col>
            <v-col cols="6"><strong>{{ weatherStore.data.wind_speed }} m/s</strong></v-col>
          </v-row>
        </v-card-text>
      </v-card>

    </v-card>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useWeatherStore } from '../../core/weather'

const weatherStore = useWeatherStore()
const cityInput = ref('Paryż')

const handleSearch = () => {
  if (cityInput.value.trim()) {
    weatherStore.fetchWeather(cityInput.value.trim())
  }
}
</script>