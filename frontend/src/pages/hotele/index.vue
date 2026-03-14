<template>
  <v-container class="mt-5">
    <div class="text-left mb-4">
      <v-btn variant="text" to="/" prepend-icon="mdi-arrow-left">Wróć do menu</v-btn>
    </div>

    <v-card class="pa-5 mx-auto mb-6" max-width="800" elevation="3">
      <h2 class="text-h5 mb-4"><v-icon>mdi-bed</v-icon> Wyszukiwarka Hoteli</h2>

      <v-row>
        <v-col cols="12" md="4">
          <v-text-field v-model="searchParams.city" label="Miasto (np. Warszawa)" variant="outlined" hide-details></v-text-field>
        </v-col>
        <v-col cols="12" md="4">
          <v-text-field v-model="searchParams.checkIn" label="Zameldowanie" type="date" variant="outlined" hide-details></v-text-field>
        </v-col>
        <v-col cols="12" md="4">
          <v-text-field v-model="searchParams.checkOut" label="Wymeldowanie" type="date" variant="outlined" hide-details></v-text-field>
        </v-col>
      </v-row>

      <v-btn color="secondary" size="large" class="mt-6" block :loading="hotelsStore.isLoading" @click="handleSearch">
        Szukaj Noclegu
      </v-btn>
    </v-card>

    <v-alert v-if="hotelsStore.error" type="error" class="mb-4 mx-auto" max-width="800" variant="tonal">
      {{ hotelsStore.error }}
    </v-alert>

    <div v-if="hotelsStore.data && hotelsStore.data.length > 0" class="mx-auto" style="max-width: 800px;">
      <h3 class="mb-4">Dostępne hotele:</h3>
      <v-card v-for="(hotel, index) in hotelsStore.data" :key="index" class="mb-3 pa-4" elevation="1" hover>
        <v-row align="center">
          <v-col cols="12" sm="5"><strong>{{ hotel.name }}</strong></v-col>
          <v-col cols="12" sm="3">⭐ Ocena: {{ hotel.rating }}/10</v-col>
          <v-col cols="12" sm="4" class="text-right text-h6 text-primary">{{ hotel.price }} {{ hotel.currency }}</v-col>
        </v-row>
      </v-card>
    </div>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useHotelsStore } from './store'

const hotelsStore = useHotelsStore()
const searchParams = ref({
  city: 'Warszawa',
  checkIn: new Date().toISOString().split('T')[0],
  checkOut: new Date(Date.now() + 86400000).toISOString().split('T')[0] // Jutro
})

const handleSearch = () => {
  if (searchParams.value.city && searchParams.value.checkIn && searchParams.value.checkOut) {
    hotelsStore.fetchHotels(searchParams.value.city, searchParams.value.checkIn, searchParams.value.checkOut)
  }
}
</script>