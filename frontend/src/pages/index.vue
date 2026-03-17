<template>
      <v-app>
                <v-btn
          icon
          position="fixed"
          location="top right"
          class="theme-toggle-btn"
          @click="toggleTheme"
          elevation="4"
        >
          <span :style="{
            fontSize: '30px',
            lineHeight: '1',
            color: 'white',
            display: 'inline-block',
            transform: !isDark ? 'translateX(-2px)' : 'none'
          }">
            {{ isDark ? '☀' : '☾' }}
          </span>
        </v-btn>

    <div class="split-layout" :class="{ 'light-mode': !isDark }">
      <div
            class="left-panel"
            :style="{
              backgroundImage: showResults
                ? 'none'
                : `${isDark
                    ? 'linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.6))'
                    : 'linear-gradient(rgba(255,255,255,0.1), rgba(255,255,255,0.1))'}, url(${currentBg})`
            }"
            :class="{ 'results-bg': showResults }"
          >

        <v-fade-transition>
  <div v-if="!showResults" class="hero-content pa-5 pa-md-10 flex-grow-1 d-flex flex-column justify-center align-start">

    <h1
      class="script-title text-white mb-4 mb-md-6 text-h3 text-md-h1"
      :style="{
        textShadow: isDark
          ? '-1px -2px 0 #000, 1px -1px 0 #000, -2px 2px 0 #000, 1px 1px 0 #000, 0px 0px 0px rgba(0,0,0,1)'
          : '-1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff, 1px 1px 0 #fff, 0px 0px 8px rgba(255,255,255,0.9)'
      }"
    >
      {{ selectedDestination?.en || 'Bali' }}
    </h1>

    <p
      class="text-white w-100 w-md-75 mb-6 mb-md-10"
      :style="{
        fontWeight: '700',
        fontSize: '1.5rem',
        lineHeight: '1.8',
        opacity: '1',
        textShadow: isDark
          ? '-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000, 0px 4px 10px rgba(0,0,0,0.8)'
          : '-1px -1px 0 rgba(0,0,0,0.3), 1px -1px 0 rgba(0,0,0,0.3), -1px 1px 0 rgba(0,0,0,0.3), 1px 1px 0 rgba(0,0,0,0.3)'
      }"
    >
      {{ selectedDestination?.pl || 'Wybierz destynację z panelu po prawej stronie,' }}
      to niesamowite miejsce znane z pięknych widoków, kultowych zabytków i niesamowitej natury.
    </p>

  </div>
</v-fade-transition>

        <v-fade-transition>
          <div v-if="showResults" class="dashboard-content pa-4 pa-md-8 flex-grow-1 overflow-y-auto w-100 text-white">
            <div class="d-flex flex-column flex-md-row justify-space-between align-start align-md-center mb-8 gap-4">
              <div class="mb-4 mb-md-0">
                <h2 class="text-h5 text-md-h4 font-weight-black mb-1">Twój plan wycieczki</h2>
                <div class="text-subtitle-1 text-grey-lighten-1">{{ selectedOrigin }} ➔ {{ selectedDestination?.en }} ({{ days }} dni)</div>
              </div>
              <v-btn variant="outlined" color="white" @click="showResults = false" rounded="pill" class="align-self-start align-self-md-auto">
                <v-icon left class="mr-2">mdi-arrow-left</v-icon> Wróć
              </v-btn>
            </div>

            <v-tabs v-model="activeTab" color="#ff7b00" align-tabs="start" class="mb-8 border-b border-opacity-25" bg-color="transparent" show-arrows>
              <v-tab value="plan" class="text-white"><v-icon left class="mr-2">mdi-map</v-icon> <span class="d-none d-sm-inline">Trasa & AI Plan</span></v-tab>
              <v-tab value="booking" class="text-white"><v-icon left class="mr-2">mdi-ticket</v-icon> <span class="d-none d-sm-inline">Loty & Hotele</span></v-tab>
              <v-tab value="events" class="text-white"><v-icon left class="mr-2">mdi-calendar-star</v-icon> <span class="d-none d-sm-inline">Wydarzenia</span></v-tab>
              <v-tab value="assistant" class="text-white"><v-icon left class="mr-2">mdi-robot</v-icon> <span class="d-none d-sm-inline">Asystent</span></v-tab>
            </v-tabs>

            <v-window v-model="activeTab" class="bg-transparent">

              <v-window-item value="plan">
                <v-card class="mb-6 overflow-hidden rounded-xl bg-surface-variant border-opacity-25" elevation="0" border>
                  <div ref="mapContainer" class="dark-map" style="height: 350px; width: 100%;"></div>
                </v-card>

                <v-card class="pa-5 pa-md-8 rounded-xl glass-card text-white" elevation="0" border>
                  <div class="d-flex align-center mb-6">
                    <v-icon color="#ff7b00" size="32" class="mr-3">mdi-sparkles</v-icon>
                    <h3 class="text-h6 text-md-h5 font-weight-bold">Wygenerowany Plan Llama 3.1</h3>
                  </div>
                  <v-divider class="mb-6 border-opacity-25"></v-divider>

                  <div v-if="aiLoading" class="text-center pa-8">
                    <v-progress-circular indeterminate color="#ff7b00" size="50"></v-progress-circular>
                    <div class="mt-4 text-grey-lighten-1">Trwa układanie planu...</div>
                  </div>
                  <div v-else v-html="aiContent" class="ai-content text-grey-lighten-2"></div>
                </v-card>
              </v-window-item>

              <v-window-item value="booking">
                <v-row>
                  <v-col cols="12" md="6">
                    <v-card class="pa-5 pa-md-6 rounded-xl glass-card text-white h-100" elevation="0" border>
                      <h3 class="text-h6 font-weight-bold mb-6 d-flex align-center">
                        <v-icon color="#ff7b00" class="mr-3">mdi-airplane</v-icon> Najtańsze Loty
                      </h3>
                      <div v-if="flightsStore.isLoading" class="text-center pa-5"><v-progress-circular indeterminate color="#ff7b00"></v-progress-circular></div>
                      <div v-else-if="flightsStore.data && flightsStore.data.length > 0">
                        <v-card v-for="(flight, i) in flightsStore.data" :key="i" class="mb-4 pa-4 pa-md-5 rounded-lg flight-hotel-card text-white" elevation="0">
                          <div class="d-flex justify-space-between align-center">
                            <div>
                              <div class="font-weight-bold text-body-1">{{ flight.airline }}</div>
                              <div class="text-caption text-grey-lighten-1 mt-1">
                                <v-icon size="x-small" class="mr-1">mdi-clock-outline</v-icon>{{ flight.departure_time }} ➔ {{ flight.arrival_time }}
                              </div>
                            </div>
                            <div class="text-subtitle-1 text-md-h6 text-green-accent-3 font-weight-black">{{ Math.round(flight.price) }} <span class="text-caption">PLN</span></div>
                          </div>
                        </v-card>
                      </div>
                      <div v-else class="text-grey-lighten-1">Brak wyników lotów.</div>
                    </v-card>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-card class="pa-5 pa-md-6 rounded-xl glass-card text-white h-100" elevation="0" border>
                      <h3 class="text-h6 font-weight-bold mb-6 d-flex align-center">
                        <v-icon color="#ff7b00" class="mr-3">mdi-bed</v-icon> Polecane Hotele
                      </h3>
                      <div v-if="hotelsStore.isLoading" class="text-center pa-5"><v-progress-circular indeterminate color="#ff7b00"></v-progress-circular></div>
                      <div v-else-if="hotelsStore.data && hotelsStore.data.length > 0">
                        <v-card v-for="(hotel, i) in hotelsStore.data" :key="i" class="mb-4 pa-4 pa-md-5 rounded-lg flight-hotel-card text-white" elevation="0">
                          <div class="d-flex justify-space-between align-center">
                            <div>
                              <div class="font-weight-bold text-body-1">{{ hotel.name }}</div>
                              <div class="text-caption text-amber mt-1">
                                <v-icon size="x-small" class="mr-1">mdi-star</v-icon> {{ hotel.rating }}/10
                              </div>
                            </div>
                            <div class="text-subtitle-1 text-md-h6 font-weight-black">{{ Math.round(hotel.price) }} <span class="text-caption">PLN</span></div>
                          </div>
                        </v-card>
                      </div>
                      <div v-else class="text-grey-lighten-1">Brak wyników hoteli.</div>
                    </v-card>
                  </v-col>
                </v-row>
              </v-window-item>

              <v-window-item value="events">
                <v-row v-if="events.length > 0">
                  <v-col v-for="(event, i) in events" :key="i" cols="12" sm="6" md="4">
                    <v-card rounded="xl" hover :href="event.url" target="_blank" class="h-100 glass-card text-white border-0 overflow-hidden" elevation="4">
                      <v-img :src="event.image" height="180" cover v-if="event.image"></v-img>
                      <v-card-text class="pa-5">
                        <div class="font-weight-bold mb-3 text-body-1">{{ event.name }}</div>
                        <div class="text-caption text-amber"><v-icon size="small" class="mr-1">mdi-calendar</v-icon> {{ event.date }}</div>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
                <div v-else class="text-center pa-8 text-grey-lighten-1 glass-card rounded-xl">Brak wydarzeń w tym terminie.</div>
              </v-window-item>

              <v-window-item value="assistant">
                <v-row>
                  <v-col cols="12" md="8">
                    <v-card class="d-flex flex-column rounded-xl glass-card text-white border-0" min-height="500" height="100%">
                      <v-card-title class="pa-4 pa-md-5 border-b border-opacity-25 d-flex align-center">
                        <v-icon left color="#ff7b00" class="mr-2">mdi-chat</v-icon> Twój Przewodnik AI
                      </v-card-title>

                      <div class="flex-grow-1 overflow-y-auto pa-4 pa-md-5 chat-scroll-area" id="chat-container">
                        <div v-for="(msg, i) in chatMessages" :key="i" :class="msg.role === 'user' ? 'text-right' : 'text-left'" class="mb-4">
                          <v-sheet :color="msg.role === 'user' ? '#ff7b00' : 'rgba(255,255,255,0.1)'" class="text-white pa-3 pa-md-4 d-inline-block text-body-2 text-md-body-1" :rounded="msg.role === 'user' ? 'xl xl-0 xl xl' : 'xl xl xl xl-0'" style="max-width: 90%;">
                            {{ msg.text }}
                          </v-sheet>
                        </div>
                        <div v-if="chatLoading" class="text-left mb-4">
                          <v-sheet color="rgba(255,255,255,0.1)" rounded="xl xl xl xl-0" class="pa-3 pa-md-4 d-inline-block text-white text-body-2 text-md-body-1">
                            <v-progress-circular indeterminate size="16" color="#ff7b00" class="mr-2"></v-progress-circular> Pisze...
                          </v-sheet>
                        </div>
                      </div>

                      <div class="pa-3 pa-md-4 border-t border-opacity-25 mt-auto">
                        <v-text-field v-model="chatInput" placeholder="Napisz do asystenta..." variant="solo" density="comfortable" hide-details @keyup.enter="sendChatMessage" rounded="pill" bg-color="rgba(255,255,255,0.1)" class="text-white">
                          <template v-slot:append-inner>
                            <v-btn icon="mdi-send" color="#ff7b00" variant="text" @click="sendChatMessage" :disabled="!chatInput.trim()"></v-btn>
                          </template>
                        </v-text-field>
                      </div>
                    </v-card>
                  </v-col>

                  <v-col cols="12" md="4">
                    <v-card class="pa-5 pa-md-6 rounded-xl glass-card text-white h-100 border-0" elevation="0">
                      <h2 class="text-h6 text-md-h5 font-weight-bold mb-6 text-center d-flex justify-center align-center">
                        <v-icon color="amber" class="mr-2">mdi-weather-partly-cloudy</v-icon> Pogoda
                      </h2>
                      <div v-if="weatherStore.isLoading" class="text-center pa-5"><v-progress-circular indeterminate color="amber"></v-progress-circular></div>
                      <div v-else class="d-flex flex-column gap-3">
                        <div v-for="(day, index) in weatherStore.data.slice(0,5)" :key="index" class="pa-3 pa-md-4 text-center rounded-lg weather-card d-flex align-center justify-space-between">
                          <div class="font-weight-bold text-caption weather-date">{{ day.date }}</div>
                          <div class="d-flex align-center">
                            <div class="text-h6 text-md-h5 mr-2 mr-md-3">{{ day.icon }}</div>
                            <div class="text-subtitle-1 text-md-h6 font-weight-black">{{ Math.round(day.temperature) }}°C</div>
                          </div>
                        </div>
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
          <h2 class="text-h5 text-md-h4 font-weight-bold text-white mb-2">Zaplanuj Lot</h2>
          <p class="text-grey-lighten-1 text-subtitle-2">Szybko, prosto i z asystą AI.</p>
        </div>

        <div class="form-inputs-wrapper d-flex flex-column gap-6">
          <v-autocomplete v-model="selectedOrigin" :items="polishAirports" item-title="name" item-value="code"
            label="Skąd wylatujesz?" variant="underlined" prepend-inner-icon="mdi-map-marker" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-autocomplete>

          <v-autocomplete v-model="selectedDestination" :items="popularDestinations" item-title="en" return-object
            label="Gdzie lecisz?" variant="underlined" prepend-inner-icon="mdi-airplane-landing" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-autocomplete>

          <v-text-field v-model="startDate" label="Data wylotu" type="date" variant="underlined" prepend-inner-icon="mdi-calendar" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-text-field>

          <v-text-field v-model.number="days" label="Czas trwania (dni)" type="number" min="1" max="30" variant="underlined" prepend-inner-icon="mdi-clock-outline" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-text-field>
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
            Wyszukaj
            <v-icon right class="ml-2">mdi-magnify</v-icon>
          </v-btn>
        </div>
      </div>
    </div>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useWeatherStore } from '../core/weather'
import { useFlightsStore } from '../core/flights'
import { useHotelsStore } from '../core/hotels'
import { useTheme } from 'vuetify'

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

const theme = useTheme()
const isDark = ref(true)

const toggleTheme = () => {
  isDark.value = !isDark.value
  theme.global.name.value = isDark.value ? 'dark' : 'light'
}

const weatherStore = useWeatherStore()
const flightsStore = useFlightsStore()
const hotelsStore = useHotelsStore()

const polishAirports = ref<any[]>([])
const popularDestinations = ref<any[]>([])

const selectedOrigin = ref<string | null>(null)
const selectedDestination = ref<any>(null)
const startDate = ref(new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0])
const days = ref(5)

const showResults = ref(false)
const activeTab = ref('plan')

const isReady = ref(false) // Dodajemy flagę gotowości

// 1. Zmieniamy computed tak, by nie zwracał nic, dopóki nie mamy celu
// 1. Importujemy listę wszystkich zdjęć z folderu (na górze skryptu)
const images = import.meta.glob('../assets/destinations/*.jpg', { eager: true, import: 'default' })

const currentBg = computed(() => {
  if (!selectedDestination.value) return ''

  const cityName = selectedDestination.value.en
  const path = `../assets/destinations/${cityName}.jpg`
  const fallbackPath = `../assets/destinations/Paris.jpg`

  // Sprawdzamy, czy klucz (ścieżka) istnieje w zaimportowanych plikach
  // Jeśli tak - zwracamy go, jeśli nie - zwracamy Paryż
  return images[path] || images[fallbackPath]
})

onMounted(async () => {
  try {
    const airportsRes = await fetch('http://127.0.0.1:8000/api/airports')
    polishAirports.value = await airportsRes.json()
    if (polishAirports.value.length > 0) selectedOrigin.value = 'WAW'

    const destRes = await fetch('http://127.0.0.1:8000/api/destinations')
    popularDestinations.value = await destRes.json()

    if (popularDestinations.value.length > 0) {
      selectedDestination.value = popularDestinations.value[0]

      // 2. Preloading: Czekamy aż zdjęcie faktycznie się pobierze
      const img = new Image()
      img.src = currentBg.value
      img.onload = () => {
        isReady.value = true // Pokaż tło dopiero gdy zdjęcie jest w pamięci
      }
    }
  } catch (error) {
    console.error('Błąd ładowania:', error)
  }
})

const aiContent = ref('')
const aiLoading = ref(false)

const chatInput = ref('')
const chatLoading = ref(false)
const chatMessages = ref<{role: string, text: string}[]>([])

const events = ref<any[]>([])

const mapContainer = ref(null)
let olMap: Map | null = null
let vectorLayer: VectorLayer<VectorSource> | null = null

onMounted(async () => {
  try {
    const airportsRes = await fetch('http://127.0.0.1:8000/api/airports')
    polishAirports.value = await airportsRes.json()
    if (polishAirports.value.length > 0) selectedOrigin.value = 'WAW'

    const destRes = await fetch('http://127.0.0.1:8000/api/destinations')
    popularDestinations.value = await destRes.json()
    if (popularDestinations.value.length > 0) selectedDestination.value = popularDestinations.value[0]
  } catch (error) {
    console.error('Błąd ładowania:', error)
  }
})

watch(activeTab, async (newVal) => {
  if (newVal === 'plan' && showResults.value) {
    await nextTick()
    if (olMap) olMap.updateSize()
    else await drawMap()
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

  chatMessages.value = [
    { role: 'ai', text: `Cześć! Gotowy na podróż do ${selectedDestination.value.pl}? W czym mogę pomóc?` }
  ]

  const checkOutDate = calculateCheckOutDate(startDate.value, days.value)

  weatherStore.fetchWeather(selectedDestination.value.en, startDate.value, days.value)
  flightsStore.fetchFlights(selectedOrigin.value, selectedDestination.value.airport, startDate.value)
  hotelsStore.fetchHotels(selectedDestination.value.en, startDate.value, checkOutDate)

  setTimeout(() => drawMap(), 300)

  fetchExtras()
  generateAiItinerary()
}

const generateAiItinerary = async () => {
  aiLoading.value = true
  aiContent.value = ''
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/itinerary?city=${selectedDestination.value.en}&days=${days.value}`)
    const json = await res.json()
    aiContent.value = json.data.replace(/```html/g, '').replace(/```/g, '')
  } catch (e) {
    aiContent.value = "Błąd generowania."
  } finally {
    aiLoading.value = false
  }
}

const sendChatMessage = async () => { /* Logika z pierwotnego pliku */ }
const fetchExtras = async () => { /* Logika z pierwotnego pliku */ }
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
  await nextTick()
  if (!mapContainer.value) return

  if (!olMap) {
    vectorLayer = new VectorLayer({ source: new VectorSource() })
    olMap = new Map({
      target: mapContainer.value,
      layers: [new TileLayer({ source: new OSM() }), vectorLayer],
      view: new View({ center: fromLonLat([20, 50]), zoom: 4 })
    })
  }

  const originObj = polishAirports.value.find(a => a.code === selectedOrigin.value)
  const destObj = selectedDestination.value

  if (originObj && destObj && vectorLayer) {
    const source = vectorLayer.getSource()
    if(source) source.clear()

    const curvedCoords = calculateFlightArc([originObj.lon, originObj.lat], [destObj.lon, destObj.lat]);
    const flightLine = new Feature({ geometry: new LineString(curvedCoords) });
    flightLine.setStyle(new Style({ stroke: new Stroke({ color: '#ff7b00', width: 3 }) }))
    source.addFeature(flightLine);

    const originMarker = new Feature({ geometry: new Point(fromLonLat([originObj.lon, originObj.lat])) });
    const destMarker = new Feature({ geometry: new Point(fromLonLat([destObj.lon, destObj.lat])) });
    source.addFeature(originMarker);
    source.addFeature(destMarker);

    olMap.getView().fit(source.getExtent(), { padding: [60, 60, 60, 60], maxZoom: 6, duration: 1500 })
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Playball&family=Inter:wght@300;400;500;700&display=swap');

/* GLOBALNA TYPOGRAFIA */
body, .v-application {
  font-family: 'Inter', sans-serif !important;
}

/* =========================================
   GŁÓWNY UKŁAD (MOBILE FIRST)
   ========================================= */
.split-layout {
  display: flex;
  flex-direction: column; /* Na telefonie panele są jeden pod drugim */
  min-height: 100vh;
  width: 100vw;
  background-color: #0f1319;
  overflow-x: hidden;
}

/* LEWY PANEL (HERO / WYNIKI) */
.left-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-size: cover;
  background-position: center;
  transition: all 0.5s ease-in-out;
  position: relative;
  min-height: 60vh; /* Na telefonie widok startowy zajmie 60% ekranu, resztę widać formularz */
}

.results-bg {
  background: #121822 !important;
}

/* PRAWY PANEL (FORMULARZ BOCZNY) */
.form-panel {
  width: 100%; /* Na telefonie zajmuje całą szerokość */
  background: linear-gradient(160deg, #37475c 0%, #222d3d 100%);
  display: flex;
  flex-direction: column;
  z-index: 10;
}

/* =========================================
   UKŁAD DESKTOPOWY (Powyżej 960px)
   ========================================= */
@media (min-width: 960px) {
  .split-layout {
    flex-direction: row; /* Panele obok siebie */
    height: 100vh; /* Sztywna wysokość ekranu */
    overflow: hidden; /* Blokujemy przewijanie całej strony... */
  }

  .left-panel {
    height: 100vh;
    overflow-y: auto; /* ...i pozwalamy przewijać tylko lewy panel z wynikami */
  }

  .form-panel {
    width: 440px; /* Sztywna szerokość formularza */
    flex-shrink: 0; /* Zapobiega zgniataniu formularza */
    box-shadow: -15px 0 40px rgba(0,0,0,0.3);
  }
}

/* =========================================
   KOMPONENTY I EFEKTY WIZUALNE
   ========================================= */

/* Glassmorphism */
.glass-card {
  background: rgba(255, 255, 255, 0.03) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

/* Interaktywne Karty (Loty, Hotele) */
.flight-hotel-card, .weather-card {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.05) !important;
  transition: background 0.2s ease, transform 0.2s ease;
}

.flight-hotel-card:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  transform: translateY(-2px);
}

/* Typografia Ozdobna */
.script-title {
  font-family: 'Playball', cursive;
  font-size: clamp(4rem, 8vw, 8rem); /* Responsywny font: min 4rem, max 8rem w zależności od ekranu */
  line-height: 1;
  text-shadow: 2px 4px 15px rgba(0,0,0,0.3);
}

/* Zmiany Vuetify & Pomocnicze */
.custom-input .v-field__input { font-size: 1.1rem; padding-top: 10px; padding-bottom: 5px; }
.custom-shadow { box-shadow: 0 10px 25px rgba(255, 123, 0, 0.4) !important; }
.hover-scale { transition: transform 0.2s; }
.hover-scale:hover { transform: scale(1.02); }
.gap-6 { gap: 24px; }
.gap-8 { gap: 32px; }

/* Stylowanie treści generowanej przez AI */
.ai-content h1, .ai-content h2, .ai-content h3 { color: #ff7b00; margin-top: 20px; margin-bottom: 10px; font-weight: 600; }
.ai-content p { margin-bottom: 12px; line-height: 1.6; }
.ai-content ul { padding-left: 20px; margin-bottom: 20px; }
.ai-content li { margin-bottom: 8px; }

/* Magiczny tryb ciemny dla mapy */
.dark-map {
  filter: invert(100%) hue-rotate(180deg) brightness(85%) contrast(90%);
  border-radius: inherit; /* Żeby mapa nie wychodziła poza zaokrąglone rogi v-card */
}

/* Zakładki Vuetify */
.v-tab { text-transform: none !important; font-weight: 500; letter-spacing: 0.5px; font-size: 1rem; }
.v-slide-group__content { padding-bottom: 2px; }

/* Paski przewijania (Scrollbar) dla ciemnego UI */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.1); }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.4); }

/* =========================================
   STYLE DLA TRYBU JASNEGO (LIGHT MODE)
   ========================================= */

/* Przycisk przełącznika - baza dla obu trybów */
.theme-toggle-btn {
  top: 20px;
  right: 20px;
  z-index: 1000;
  transition: background-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;
}

/* Specyficzny kolor przycisku dla trybu ciemnego */
:not(.light-mode) .theme-toggle-btn {
  background-color: #ff7b00 !important;
  color: white !important;
}

/* Kolor ikony przycisku przyciągający wzrok w trybie jasnym */
.light-mode .theme-toggle-btn {
  background-color: #ffffff !important;
  color: #ff7b00 !important;
  box-shadow: 0 4px 12px rgba(255,123,0,0.2) !important;
}

/* TŁO WYNIKÓW W TRYBIE JASNYM - to rozwiązuje problem "czarnej dziury" */
.light-mode .results-bg {
  background: #f4f7fb !important;
}

/* Poprawiona czytelność tekstu w trybie jasnym */
.light-mode .left-panel .text-white,
.light-mode .left-panel .text-grey-lighten-2,
.light-mode .hero-content p {
  color: #1a202c !important; /* Ciemny grafit zamiast czystej czerni (wygląda lepiej) */
  /* Biała "otoczka" (outline) wokół liter, aby odciąć je od jasnego zdjęcia */
  text-shadow:
    -1px -1px 0 #fff,
     1px -1px 0 #fff,
    -1px  1px 0 #fff,
     1px  1px 0 #fff,
     0px  0px 10px rgba(255,255,255,0.8) !important;
  -webkit-text-stroke: 0px !important;
  font-weight: 700 !important;
}

/* Specjalne traktowanie dla głównego tytułu (Paris / Bali) */
.light-mode .script-title {
  color: #ff7b00 !important; /* Pozostawiamy pomarańczowy, by pasował do reszty */
  text-shadow:
    -2px -2px 0 #fff,
     2px -2px 0 #fff,
    -2px  2px 0 #fff,
     2px  2px 0 #fff,
     0px 4px 10px rgba(0,0,0,0.1) !important;
}

.light-mode .hero-content p {
  color: #000000 !important;
  font-weight: 600; /* Pogrubienie również w trybie jasnym */
  opacity: 1 !important; /* Pełna widoczność dla czerni */
}

/* Prawy panel (formularz) */
.light-mode .form-panel {
  background: linear-gradient(160deg, #ffffff 0%, #e2e8f0 100%) !important;
  box-shadow: -10px 0 30px rgba(0,0,0,0.05);
}
.light-mode .form-panel h2, .light-mode .form-panel p { color: #1a202c !important; }

/* Inputy Vuetify w jasnym formularzu */
.light-mode .custom-input .v-label { color: #4a5568 !important; }
.light-mode .custom-input .v-field__input { color: #1a202c !important; }

/* Karty (szkło) */
.light-mode .glass-card {
  background: rgba(0, 0, 0, 0.03) !important;
  border: 1px solid rgba(0, 0, 0, 0.08) !important;
  color: #2d3748 !important;
}

/* Karty lotów, hoteli i pogody */
.light-mode .flight-hotel-card, .light-mode .weather-card {
  background: white !important;
  border: 1px solid #e2e8f0 !important;
  color: #4a5568 !important;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
}

/* Zakładki Vuetify */
.light-mode .v-tab { color: #4a5568 !important; }
.light-mode .v-tab--selected { color: #ff7b00 !important; }

/* Dymki chatbota w trybie jasnym */
.light-mode .chat-scroll-area .v-sheet:not([color="#ff7b00"]) {
  background-color: #e2e8f0 !important;
  color: #2d3748 !important;
}

/* Naprawa inputa w czacie dla trybu jasnego */
.light-mode #chat-container + div .v-text-field {
  background-color: #ffffff !important;
  border-radius: 999px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.light-mode #chat-container + div .v-field__input {
  color: #2d3748 !important;
}

/* Naprawa ciemnej mapy w jasnym trybie */
.light-mode .dark-map { filter: none !important; }

/* =========================================
   EFEKT NASWIETLENIA ZDJĘCIA (EXPOSED EFFECT)
   ========================================= */

.left-panel:not(.results-bg) {
  position: relative;
}

.left-panel:not(.results-bg)::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: inherit;
  filter: sepia(0.3) saturate(1.2) contrast(1.1) brightness(1.05);
  mix-blend-mode: soft-light;
  opacity: 0.8;
  z-index: 1;
}

.hero-content {
  z-index: 2;
  position: relative;
}
</style>