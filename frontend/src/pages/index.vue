<template>
  <v-container class="text-center mt-10">
    <v-card class="pa-8 mx-auto" max-width="600" elevation="3">
      <h1 class="text-h4 text-primary mb-4">{{ $t('welcome') }}</h1>
      <p class="text-body-1 mb-8">Wybierz moduł, z którego chcesz skorzystać:</p>

      <v-row justify="center">
        <v-col cols="12" sm="6">
          <v-btn
            color="primary"
            size="x-large"
            block
            prepend-icon="mdi-weather-cloudy"
            to="/pogoda"
          >
            Moduł Pogody
          </v-btn>
        </v-col>

        <v-col cols="12" sm="6">
          <v-btn
            color="secondary"
            size="x-large"
            block
            disabled
          >
            Loty (Wkrótce)
          </v-btn>
        </v-col>
      </v-row>
    </v-card>
  </v-container>
</template>