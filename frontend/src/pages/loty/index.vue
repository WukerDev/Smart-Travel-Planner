<template>
  <v-container class="mt-5">
    <div class="text-left mb-4">
      <v-btn variant="text" to="/" prepend-icon="mdi-arrow-left">
        Wróć do menu
      </v-btn>
    </div>

    <v-card class="pa-5 mx-auto mb-6" max-width="800" elevation="3">
      <h2 class="text-h5 mb-4"><v-icon>mdi-airplane</v-icon> Wyszukiwarka Lotów</h2>

      <v-row>
        <v-col cols="12" md="4">
          <v-text-field
            v-model="searchParams.origin"
            label="Skąd (np. WAW)"
            variant="outlined"
            hide-details
          ></v-text-field>
        </v-col>

        <v-col cols="12" md="4">
          <v-text-field
            v-model="searchParams.destination"
            label="Dokąd (np. CDG)"
            variant="outlined"
            hide-details
          ></v-text-field>
        </v-col>

        <v-col cols="12" md="4">
          <v-text-field
            v-model="searchParams.date"
            label="Data wylotu"
            type="date"
            variant="outlined"
            hide-details
          ></v-text-field>
        </v-col>
      </v-row>

      <v-btn
        color="primary"
        size="large"
        class="mt-6"
        block
        :loading="flightsStore.isLoading"
        @click="handleSearch"
      >
        Szukaj Połączeń
      </v-btn>
    </v-card>

    <v-alert v-if="flightsStore.error" type="error" class="mb-4 mx-auto" max-width="800" variant="tonal">
      {{ flightsStore.error }}
    </v-alert>

    <div v-if="flightsStore.data && flightsStore.data.length > 0" class="mx-auto" style="max-width: 800px;">
      <h3 class="mb-4">Znalezione loty:</h3>

      <v-card
        v-for="(flight, index) in flightsStore.data"
        :key="index"
        class="mb-3 pa-4"
        elevation="1"
        hover
      >
        <v-row align="center">
          <v-col cols="12" sm="3">
            <strong>Linia:</strong> <br>{{ flight.airline || 'Nieznana' }}
          </v-col>
          <v-col cols="12" sm="3">
            <strong>Wylot:</strong> <br>{{ flight.departure_time }}
          </v-col>
          <v-col cols="12" sm="3">
            <strong>Przylot:</strong> <br>{{ flight.arrival_time }}
          </v-col>
          <v-col cols="12" sm="3" class="text-right text-h6 text-green-darken-2">
            {{ flight.price }} PLN
          </v-col>
        </v-row>
      </v-card>
    </div>

    <v-alert v-else-if="flightsStore.data && flightsStore.data.length === 0" type="info" class="mx-auto" max-width="800" variant="tonal">
      Brak lotów dla podanych kryteriów.
    </v-alert>

  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useFlightsStore } from './store'

const flightsStore = useFlightsStore()
const searchParams = ref({
  origin: 'WAW',
  destination: 'CDG',
  date: new Date().toISOString().split('T')[0]
})

const handleSearch = () => {
  if (searchParams.value.origin && searchParams.value.destination && searchParams.value.date) {
    flightsStore.fetchFlights(
      searchParams.value.origin,
      searchParams.value.destination,
      searchParams.value.date
    )
  }
}
</script>