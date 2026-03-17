<template>
  <v-app>
    <div style="position: fixed; top: 16px; right: 16px; z-index: 1000; display: flex; gap: 12px;">
      <v-btn icon class="theme-toggle-btn" @click="toggleLanguage" elevation="4">
        <span style="font-weight: bold; font-size: 16px; color: white;">
          {{ locale === 'pl' ? 'EN' : 'PL' }}
        </span>
      </v-btn>

      <v-btn icon class="theme-toggle-btn" @click="toggleTheme" elevation="4">
        <span :style="{ fontSize: '30px', lineHeight: '1', color: 'white', display: 'inline-block', transform: !isDark ? 'translateX(-2px)' : 'none' }">
          {{ isDark ? '☀' : '☾' }}
        </span>
      </v-btn>
    </div>

    <div class="split-layout" :class="{ 'light-mode': !isDark }">

      <div
        class="left-panel"
        :style="{
          backgroundImage: showResults
            ? 'none'
            : `${isDark
                ? 'linear-gradient(to bottom, rgba(0,0,0,0) 60%, rgba(0,0,0,0.85) 100%)'
                : 'linear-gradient(to bottom, rgba(255,255,255,0) 75%, rgba(255,255,255,0.75) 100%)'}, url(${currentBg})`
        }"
        :class="{ 'results-bg': showResults }"
      >

        <v-fade-transition>
          <div v-if="!showResults" class="hero-content pa-5 pa-md-12 flex-grow-1 d-flex flex-column justify-end align-start pb-md-24">
            <h1 class="script-title mb-4">
              {{ selectedDestination?.[locale] || $t('hero.title') }}
            </h1>
            <p class="hero-subtitle w-100 w-md-75 mb-0">
              {{ heroContent?.subtitle || $t('hero.subtitle') }}
            </p>
          </div>
        </v-fade-transition>

        <v-fade-transition>
          <div v-if="showResults" class="dashboard-content pa-4 pa-md-8 flex-grow-1 overflow-y-auto w-100 text-white">

            <div class="d-flex flex-column flex-md-row justify-space-between align-start align-md-center mb-8 gap-4">
              <div class="mb-4 mb-md-0">
                <h2 class="text-h5 text-md-h4 font-weight-black mb-1 text-high-emphasis">{{ $t('planTitle') }}</h2>
                <div class="text-subtitle-1 text-medium-emphasis">{{ selectedOrigin }} ➔ {{ selectedDestination?.[locale] }} ({{ days }} {{ $t('days') }})</div>
              </div>
              <v-btn
                variant="outlined"
                color="primary"
                @click="resetSearch"
                rounded="pill"
                class="align-self-start align-self-md-auto"
              >
                <v-icon left class="mr-2">mdi-arrow-left</v-icon> {{ $t('backBtn') }}
              </v-btn>
            </div>

            <v-tabs v-model="activeTab" color="#ff7b00" align-tabs="start" class="mb-8 border-b border-opacity-25" bg-color="transparent" show-arrows>
              <v-tab value="plan" class="text-high-emphasis"><v-icon left class="mr-2">mdi-map</v-icon> <span class="d-none d-sm-inline">{{ $t('tabs.plan') }}</span></v-tab>
              <v-tab value="booking" class="text-high-emphasis"><v-icon left class="mr-2">mdi-ticket</v-icon> <span class="d-none d-sm-inline">{{ $t('tabs.booking') }}</span></v-tab>
              <v-tab value="events" class="text-high-emphasis"><v-icon left class="mr-2">mdi-calendar-star</v-icon> <span class="d-none d-sm-inline">{{ $t('tabs.events') }}</span></v-tab>
              <v-tab value="assistant" class="text-high-emphasis"><v-icon left class="mr-2">mdi-robot</v-icon> <span class="d-none d-sm-inline">{{ $t('tabs.assistant') }}</span></v-tab>
            </v-tabs>

            <v-window v-model="activeTab" class="bg-transparent">

              <v-window-item value="plan">

                <v-card class="mb-6 pa-5 pa-md-6 rounded-xl glass-card text-white" elevation="0" border>
                  <div class="d-flex align-center mb-4">
                    <v-icon color="amber" size="28" class="mr-3">mdi-weather-partly-cloudy</v-icon>
                    <h3 class="text-h6 font-weight-bold text-high-emphasis">{{ $t('weather') }}</h3>
                  </div>
                  <div v-if="weatherStore.isLoading" class="text-center pa-5"><v-progress-circular indeterminate color="amber"></v-progress-circular></div>
                  <div v-else class="d-flex flex-row overflow-x-auto gap-4 pb-2 weather-scroll">
                    <v-card
                      v-for="(day, index) in weatherStore.data.slice(0, days > 7 ? 7 : days)"
                      :key="index"
                      class="weather-card flex-grow-1 flex-shrink-0 d-flex flex-column align-center justify-center pa-4 rounded-lg text-high-emphasis"
                      elevation="0"
                      min-width="130"
                    >
                      <div class="text-caption font-weight-bold mb-2 opacity-80">{{ day.date }}</div>
                      <div class="text-h3 mb-2">{{ day.icon }}</div>
                      <div class="text-h5 font-weight-black">{{ Math.round(day.temperature) }}°C</div>
                      <div class="text-caption mt-1 text-center opacity-80" style="line-height: 1.2;">{{ day.description }}</div>
                    </v-card>
                  </div>
                </v-card>

                <v-card class="mb-6 overflow-hidden rounded-xl bg-surface-variant border-opacity-25" elevation="0" border>
                  <div ref="mapContainer" :class="{'dark-map': isDark}" style="height: 350px; width: 100%;"></div>
                </v-card>

                <v-card class="pa-5 pa-md-8 rounded-xl glass-card text-high-emphasis" elevation="0" border>
                  <div class="d-flex align-center mb-6">
                    <v-icon color="#ff7b00" size="32" class="mr-3">mdi-sparkles</v-icon>
                    <h3 class="text-h6 text-md-h5 font-weight-bold">{{ $t('aiPlan') }}</h3>
                  </div>
                  <v-divider class="mb-6 border-opacity-25"></v-divider>

                  <div v-if="aiLoading" class="text-center pa-8">
                    <v-progress-circular indeterminate color="#ff7b00" size="50"></v-progress-circular>
                    <div class="mt-4 text-medium-emphasis">{{ $t('aiLoading') }}</div>
                  </div>
                  <div v-else v-html="aiContent" class="ai-content text-medium-emphasis"></div>
                </v-card>
              </v-window-item>

              <v-window-item value="booking">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-card class="pa-5 pa-md-6 rounded-xl glass-card text-high-emphasis h-100" elevation="0" border>
                      <h3 class="text-h6 font-weight-bold mb-6 d-flex align-center">
                        <v-icon color="#ff7b00" class="mr-3">mdi-airplane</v-icon> {{ $t('flights') }}
                      </h3>
                      <div v-if="flightsStore.isLoading" class="text-center pa-5"><v-progress-circular indeterminate color="#ff7b00"></v-progress-circular></div>
                      <div v-else-if="flightsStore.data && flightsStore.data.length > 0">
                        <v-card v-for="(flight, i) in flightsStore.data" :key="i" class="mb-4 pa-4 pa-md-5 rounded-lg flight-hotel-card text-high-emphasis" elevation="0">
                          <div class="d-flex justify-space-between align-center">
                            <div>
                              <div class="font-weight-bold text-body-1">{{ flight.airline }}</div>
                              <div class="text-caption text-medium-emphasis mt-1">
                                <v-icon size="x-small" class="mr-1">mdi-clock-outline</v-icon>{{ flight.departure_time }} ➔ {{ flight.arrival_time }}
                              </div>
                            </div>
                            <div class="text-subtitle-1 text-md-h6 text-green-darken-1 font-weight-black">{{ Math.round(flight.price) }} <span class="text-caption">PLN</span></div>
                          </div>
                        </v-card>
                      </div>
                      <div v-else class="text-medium-emphasis">{{ $t('noFlights') }}</div>
                    </v-card>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-card class="pa-5 pa-md-6 rounded-xl glass-card text-high-emphasis h-100" elevation="0" border>
                      <h3 class="text-h6 font-weight-bold mb-6 d-flex align-center">
                        <v-icon color="#ff7b00" class="mr-3">mdi-bed</v-icon> {{ $t('hotels') }}
                      </h3>
                      <div v-if="hotelsStore.isLoading" class="text-center pa-5"><v-progress-circular indeterminate color="#ff7b00"></v-progress-circular></div>
                      <div v-else-if="hotelsStore.data && hotelsStore.data.length > 0">
                        <v-card v-for="(hotel, i) in hotelsStore.data" :key="i" class="mb-4 pa-4 pa-md-5 rounded-lg flight-hotel-card text-high-emphasis" elevation="0">
                          <div class="d-flex justify-space-between align-center">
                            <div>
                              <div class="font-weight-bold text-body-1">{{ hotel.name }}</div>
                              <div class="text-caption text-amber-darken-2 mt-1 font-weight-bold">
                                <v-icon size="x-small" class="mr-1">mdi-star</v-icon> {{ hotel.rating }}/10
                              </div>
                            </div>
                            <div class="text-subtitle-1 text-md-h6 font-weight-black">{{ Math.round(hotel.price) }} <span class="text-caption">PLN</span></div>
                          </div>
                        </v-card>
                      </div>
                      <div v-else class="text-medium-emphasis">{{ $t('noHotels') }}</div>
                    </v-card>
                  </v-col>
                </v-row>
              </v-window-item>

              <v-window-item value="events">
                <v-row v-if="events.length > 0">
                  <v-col v-for="(event, i) in events" :key="i" cols="12" sm="6" md="4">
                    <v-card rounded="xl" hover :href="event.url" target="_blank" class="h-100 glass-card text-high-emphasis border-0 overflow-hidden" elevation="4">
                      <v-img :src="event.image" height="180" cover v-if="event.image"></v-img>
                      <v-card-text class="pa-5 bg-surface">
                        <div class="font-weight-bold mb-3 text-body-1">{{ event.name }}</div>
                        <div class="text-caption text-primary font-weight-bold"><v-icon size="small" class="mr-1">mdi-calendar</v-icon> {{ event.date }}</div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
                <div v-else class="text-center pa-8 text-medium-emphasis glass-card rounded-xl">{{ $t('noEvents') }}</div>
              </v-window-item>

              <v-window-item value="assistant">
                <v-row>
                  <v-col cols="12">
                    <v-card class="d-flex flex-column rounded-xl glass-card text-high-emphasis border-0" min-height="600" height="100%">
                      <v-card-title class="pa-4 pa-md-5 border-b border-opacity-25 d-flex align-center">
                        <v-icon left color="#ff7b00" class="mr-2">mdi-chat</v-icon> {{ $t('chatTitle') }}
                      </v-card-title>

                      <div class="flex-grow-1 overflow-y-auto pa-4 pa-md-5 chat-scroll-area bg-surface" id="chat-container">
                        <div v-for="(msg, i) in chatMessages" :key="i" :class="msg.role === 'user' ? 'text-right' : 'text-left'" class="mb-4">
                          <v-sheet
                            :color="msg.role === 'user' ? '#ff7b00' : 'background'"
                            :class="msg.role === 'user' ? 'text-white' : 'text-high-emphasis border'"
                            class="pa-3 pa-md-4 d-inline-block text-body-2 text-md-body-1"
                            :rounded="msg.role === 'user' ? 'xl xl-0 xl xl' : 'xl xl xl xl-0'"
                            style="max-width: 90%; white-space: pre-wrap; line-height: 1.5;"
                            elevation="1"
                          >
                            {{ msg.text }}
                          </v-sheet>
                        </div>
                        <div v-if="chatLoading" class="text-left mb-4">
                          <v-sheet color="background" rounded="xl xl xl xl-0" class="pa-3 pa-md-4 d-inline-block text-high-emphasis text-body-2 text-md-body-1 border">
                            <v-progress-circular indeterminate size="16" color="#ff7b00" class="mr-2"></v-progress-circular> {{ $t('typing') }}
                          </v-sheet>
                        </div>
                      </div>

                      <div class="pa-3 pa-md-4 border-t border-opacity-25 mt-auto bg-surface">
                        <v-text-field
                          v-model="chatInput"
                          :placeholder="$t('chatPlaceholder')"
                          variant="outlined"
                          density="comfortable"
                          hide-details
                          @keyup.enter="sendChatMessage"
                          rounded="pill"
                          bg-color="background"
                        >
                          <template v-slot:append-inner>
                            <v-btn icon="mdi-send" color="#ff7b00" variant="text" @click="sendChatMessage" :disabled="!chatInput.trim()"></v-btn>
                          </template>
                        </v-text-field>
                      </div>
                    </v-card>
                  </v-col>
                </v-row>
              </v-window-item>
            </v-window>
          </div>
        </v-fade-transition>
      </div>

      <div class="right-panel form-panel px-5 px-md-10 pt-8 pt-md-16 pb-8 pb-md-10">
        <div class="mb-8 mb-md-12">
          <h2 class="text-h5 text-md-h4 font-weight-bold text-white mb-2">{{ $t('form.title') }}</h2>
          <p class="text-grey-lighten-1 text-subtitle-2">{{ $t('form.subtitle') }}</p>
        </div>

        <div class="form-inputs-wrapper d-flex flex-column gap-6">
          <v-autocomplete v-model="selectedOrigin" :items="polishAirports" item-title="name" item-value="code"
            :label="$t('form.origin')" variant="underlined" prepend-inner-icon="mdi-map-marker" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-autocomplete>

          <v-autocomplete v-model="selectedDestination" :items="popularDestinations" :item-title="locale" return-object
            :label="$t('form.dest')" variant="underlined" prepend-inner-icon="mdi-airplane-landing" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-autocomplete>

          <v-text-field v-model="startDate" :label="$t('form.date')" type="date" variant="underlined" prepend-inner-icon="mdi-calendar" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-text-field>

          <v-text-field v-model.number="days" :label="$t('form.days')" type="number" min="1" max="30" variant="underlined" prepend-inner-icon="mdi-clock-outline" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-text-field>
        </div>

        <div class="form-footer mt-12">
          <v-btn
            color="#ff7b00"
            size="x-large"
            block
            rounded="pill"
            class="search-btn font-weight-bold text-white"
            elevation="12"
            @click="generateTrip"
            :loading="isSearching"
          >
            {{ $t('form.search') }}
            <v-icon right class="ml-2">mdi-magnify</v-icon>
          </v-btn>
        </div>
      </div>
    </div>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useTheme } from 'vuetify'
import { useWeatherStore } from '../core/weather'
import { useFlightsStore } from '../core/flights'
import { useHotelsStore } from '../core/hotels'
import { useLocationsStore } from '../core/locations'
import { useAiStore } from '../core/ai'
import { useExtrasStore } from '../core/extras'

import 'ol/ol.css'
import Map from 'ol/Map'
import View from 'ol/View'
import TileLayer from 'ol/layer/Tile'
import OSM from 'ol/source/OSM'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import Feature from 'ol/Feature'
import LineString from 'ol/geom/LineString'
import { fromLonLat } from 'ol/proj'
import Point from 'ol/geom/Point'
import { Style, Stroke, Icon } from 'ol/style'
import heroTexts from '../assets/destinations.json';
import { useI18n } from 'vue-i18n'

const theme = useTheme()
const isDark = ref(true)

const { t, locale } = useI18n()

const toggleLanguage = () => {
  locale.value = locale.value === 'pl' ? 'en' : 'pl'
}

const toggleTheme = () => {
  isDark.value = !isDark.value
  theme.global.name.value = isDark.value ? 'dark' : 'light'
}

const heroContent = computed(() => {
  const destinationKey = selectedDestination.value ? selectedDestination.value.airport : 'DEFAULT'
  // Używamy locale.value z useI18n()
  return heroTexts[destinationKey]?.[locale.value] || heroTexts['DEFAULT'][locale.value]
})

const weatherStore = useWeatherStore()
const flightsStore = useFlightsStore()
const hotelsStore = useHotelsStore()
const locationsStore = useLocationsStore()
const aiStore = useAiStore()
const extrasStore = useExtrasStore()

const { airports: polishAirports, destinations: popularDestinations } = storeToRefs(locationsStore)
const { itineraryContent: aiContent, isItineraryLoading: aiLoading, chatMessages, isChatLoading: chatLoading } = storeToRefs(aiStore)
const { events, isLoading: isSearchingExtras } = storeToRefs(extrasStore)

const selectedOrigin = ref<string | null>(null)
const selectedDestination = ref<any>(null)
const startDate = ref(new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0])
const days = ref(5)

const showResults = ref(false)
const activeTab = ref('plan')
const chatInput = ref('')

const isReady = ref(false)
const images = import.meta.glob('../assets/destinations/*.jpg', { eager: true, import: 'default' })

const currentBg = computed(() => {
  if (!selectedDestination.value) return ''
  const cityName = selectedDestination.value.en
  const path = `../assets/destinations/${cityName}.jpg`
  const fallbackPath = `../assets/destinations/Paris.jpg`
  return (images[path] as any)?.default || images[path] || (images[fallbackPath] as any)?.default || images[fallbackPath]
})

const mapContainer = ref(null)
let olMap: Map | null = null
let vectorLayer: VectorLayer<VectorSource> | null = null

onMounted(async () => {
  await locationsStore.fetchLocations()
  if (polishAirports.value.length > 0) selectedOrigin.value = 'WAW'

  if (popularDestinations.value.length > 0) {
    selectedDestination.value = popularDestinations.value[0]
    const img = new Image()
    img.src = currentBg.value
    img.onload = () => {
      isReady.value = true
    }
  }
})

watch(activeTab, async (newVal) => {
  if (newVal === 'plan' && showResults.value) {
    await nextTick()
    if (olMap) olMap.updateSize()
  }
})

const isSearching = computed(() => weatherStore.isLoading || flightsStore.isLoading || hotelsStore.isLoading)

const calculateCheckOutDate = (startDate: string, days: number) => {
  const date = new Date(startDate)
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

const generateTrip = async () => {
  if (!selectedOrigin.value || !selectedDestination.value || !days.value) return

  showResults.value = true
  activeTab.value = 'plan'

  aiStore.resetChat(selectedDestination.value.pl)

  const checkOutDate = calculateCheckOutDate(startDate.value, days.value)

  weatherStore.fetchWeather(selectedDestination.value.en, startDate.value, days.value)
  flightsStore.fetchFlights(selectedOrigin.value, selectedDestination.value.airport, startDate.value)
  hotelsStore.fetchHotels(selectedDestination.value.en, startDate.value, checkOutDate)

  await nextTick()
  await drawMap()

  await extrasStore.fetchExtras(
    selectedDestination.value.en,
    selectedDestination.value.lat,
    selectedDestination.value.lon,
    startDate.value,
    checkOutDate
  )

  addPoisToMap(extrasStore.pois)
  aiStore.generateItinerary(selectedDestination.value.en, days.value)
}
const resetSearch = () => {
  showResults.value = false
  activeTab.value = 'plan'
  chatInput.value = ''

  if (polishAirports.value.length > 0) selectedOrigin.value = 'WAW'
  if (popularDestinations.value.length > 0) selectedDestination.value = popularDestinations.value[0]

  startDate.value = new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0]
  days.value = 5

  if (olMap) {
    olMap.setTarget(undefined)
    olMap = null
  }
  vectorLayer = null
}

const sendChatMessage = async () => {
  if (!chatInput.value.trim() || chatLoading.value) return

  const msg = chatInput.value
  chatInput.value = ''
  scrollToBottomChat()

  await aiStore.sendMessage(msg, selectedDestination.value.pl)
  scrollToBottomChat()
}

const scrollToBottomChat = () => {
  setTimeout(() => {
    const box = document.getElementById('chat-container')
    if (box) box.scrollTop = box.scrollHeight
  }, 100)
}

const addPoisToMap = (pois: any[]) => {
  if (!vectorLayer) return
  const source = vectorLayer.getSource()
  if (!source) return

  const poiIcon = `data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%23FFC107' d='M12 2C8.14 2 5 5.14 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.86-3.14-7-7-7zm0 2c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm0 13.9c-1.55-2.22-3.8-5.74-4.66-8.15C6.91 8.7 7 8 7 8s.67-.14 1.45-.48c1.15.7 2.37 1.48 3.55 1.48s2.4-.78 3.55-1.48C16.33 7.86 17 8 17 8s.09.7-.34 1.75c-.86 2.41-3.11 5.93-4.66 8.15z'/%3E%3C/svg%3E`;

  pois.forEach(poi => {
    if(!poi.lon || !poi.lat) return
    const feature = new Feature({ geometry: new Point(fromLonLat([poi.lon, poi.lat])) })
    feature.setStyle(new Style({ image: new Icon({ src: poiIcon, anchor: [0.5, 1], scale: 1.2 }) }))
    source.addFeature(feature)
  })
}

const calculateFlightArc = (startLonLat: number[], endLonLat: number[]) => {
  const coords = [];
  const pointsCount = 100;
  const distanceX = endLonLat[0] - startLonLat[0];
  const distanceY = endLonLat[1] - startLonLat[1];
  const curveFactor = 0.05;

  for (let i = 0; i <= pointsCount; i++) {
    const t = i / pointsCount;
    const lon = startLonLat[0] + distanceX * t;
    const lat = startLonLat[1] + distanceY * t;
    const arcHeight = Math.sin(t * Math.PI) * (Math.abs(distanceX) * curveFactor);
    coords.push(fromLonLat([lon, lat + arcHeight]));
  }
  return coords;
}

const drawMap = async () => {
  if (!mapContainer.value) return

  if (!olMap) {
    vectorLayer = new VectorLayer({ source: new VectorSource() })
    olMap = new Map({
      target: mapContainer.value,
      layers: [new TileLayer({ source: new OSM() }), vectorLayer],
      view: new View({ center: fromLonLat([20, 50]), zoom: 4 })
    })
  }

  const originObj = polishAirports.value.find((a: any) => a.code === selectedOrigin.value)
  const destObj = selectedDestination.value

  if (originObj && destObj && vectorLayer) {
    const source = vectorLayer.getSource()
    if(source) source.clear()

    const curvedCoords = calculateFlightArc([originObj.lon, originObj.lat], [destObj.lon, destObj.lat]);
    const flightLine = new Feature({ geometry: new LineString(curvedCoords) });
    flightLine.setStyle(new Style({ stroke: new Stroke({ color: '#ff7b00', width: 3 }) }))
    source.addFeature(flightLine);

    const startIconSvg = `data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='36' height='36' viewBox='0 0 24 24'%3E%3Cpath fill='%234CAF50' d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E`;
    const destIconSvg = `data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='36' height='36' viewBox='0 0 24 24'%3E%3Cpath fill='%23F44336' d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E`;

    const originMarker = new Feature({ geometry: new Point(fromLonLat([originObj.lon, originObj.lat])) });
    originMarker.setStyle(new Style({ image: new Icon({ src: startIconSvg, anchor: [0.5, 1] }) }));
    source.addFeature(originMarker);

    const destMarker = new Feature({ geometry: new Point(fromLonLat([destObj.lon, destObj.lat])) });
    destMarker.setStyle(new Style({ image: new Icon({ src: destIconSvg, anchor: [0.5, 1] }) }));
    source.addFeature(destMarker);

    olMap.getView().fit(source.getExtent(), { padding: [60, 60, 60, 60], maxZoom: 6, duration: 1500 })
  }
}
</script>

<style>
@import '../assets/main.css';
</style>