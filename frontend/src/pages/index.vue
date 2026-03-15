<template>
  <v-app>
    <div class="split-layout">
      <div
        class="left-panel"
        :style="{ backgroundImage: showResults ? 'none' : `linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.6)), url(${currentBg})` }"
        :class="{ 'results-bg': showResults }"
      >

        <v-fade-transition>
          <div v-if="!showResults" class="hero-content pa-10 flex-grow-1 d-flex flex-column justify-center align-start">
            <h1 class="script-title text-white mb-6">{{ selectedDestination?.en || 'Bali' }}</h1>
            <p class="text-white text-body-1 w-50 mb-10" style="opacity: 0.9; line-height: 1.8;">
              {{ selectedDestination?.pl || 'Wybierz destynację z panelu po prawej stronie,' }} to niesamowite miejsce znane z pięknych widoków, kultowych zabytków i niesamowitej natury.
            </p>
          </div>
        </v-fade-transition>

        <v-fade-transition>
          <div v-if="showResults" class="dashboard-content pa-8 flex-grow-1 overflow-y-auto w-100 text-white">
            <div class="d-flex justify-space-between align-center mb-8">
              <div>
                <h2 class="text-h4 font-weight-black mb-1">Twój plan wycieczki</h2>
                <div class="text-subtitle-1 text-grey-lighten-1">{{ selectedOrigin }} ➔ {{ selectedDestination?.en }} ({{ days }} dni)</div>
              </div>
              <v-btn variant="outlined" color="white" @click="showResults = false" rounded="pill">
                <v-icon left>mdi-arrow-left</v-icon> Wróć do wyszukiwarki
              </v-btn>
            </div>

            <v-tabs v-model="activeTab" color="#ff7b00" align-tabs="start" class="mb-8 border-b border-opacity-25" bg-color="transparent">
              <v-tab value="plan" class="text-white"><v-icon left class="mr-2">mdi-map</v-icon> Trasa & AI Plan</v-tab>
              <v-tab value="booking" class="text-white"><v-icon left class="mr-2">mdi-ticket</v-icon> Loty & Hotele</v-tab>
              <v-tab value="events" class="text-white"><v-icon left class="mr-2">mdi-calendar-star</v-icon> Wydarzenia</v-tab>
              <v-tab value="assistant" class="text-white"><v-icon left class="mr-2">mdi-robot</v-icon> Asystent & Pogoda</v-tab>
            </v-tabs>

            <v-window v-model="activeTab" class="bg-transparent">
              <v-window-item value="plan">
                <v-card class="mb-6 overflow-hidden rounded-xl bg-surface-variant border-opacity-25" elevation="0" border>
                  <div ref="mapContainer" class="dark-map" style="height: 350px; width: 100%;"></div>
                </v-card>

                <v-card class="pa-8 rounded-xl glass-card text-white" elevation="0" border>
                  <div class="d-flex align-center mb-6">
                    <v-icon color="#ff7b00" size="32" class="mr-3">mdi-sparkles</v-icon>
                    <h3 class="text-h5 font-weight-bold">Wygenerowany Plan Llama 3.1</h3>
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
                    <v-card class="pa-6 rounded-xl glass-card text-white h-100" elevation="0" border>
                      <h3 class="text-h6 font-weight-bold mb-6 d-flex align-center">
                        <v-icon color="#ff7b00" class="mr-3">mdi-airplane</v-icon> Najtańsze Loty
                      </h3>
                      <div v-if="flightsStore.isLoading" class="text-center pa-5"><v-progress-circular indeterminate color="#ff7b00"></v-progress-circular></div>
                      <div v-else-if="flightsStore.data && flightsStore.data.length > 0">
                        <v-card v-for="(flight, i) in flightsStore.data" :key="i" class="mb-4 pa-5 rounded-lg flight-hotel-card text-white" elevation="0">
                          <div class="d-flex justify-space-between align-center">
                            <div>
                              <div class="font-weight-bold text-body-1">{{ flight.airline }}</div>
                              <div class="text-caption text-grey-lighten-1 mt-1">
                                <v-icon size="x-small" class="mr-1">mdi-clock-outline</v-icon>{{ flight.departure_time }} ➔ {{ flight.arrival_time }}
                              </div>
                            </div>
                            <div class="text-h6 text-green-accent-3 font-weight-black">{{ Math.round(flight.price) }} <span class="text-caption">PLN</span></div>
                          </div>
                        </v-card>
                      </div>
                      <div v-else class="text-grey-lighten-1">Brak wyników lotów.</div>
                    </v-card>
                  </v-col>

                  <v-col cols="12" md="6">
                    <v-card class="pa-6 rounded-xl glass-card text-white h-100" elevation="0" border>
                      <h3 class="text-h6 font-weight-bold mb-6 d-flex align-center">
                        <v-icon color="#ff7b00" class="mr-3">mdi-bed</v-icon> Polecane Hotele
                      </h3>
                      <div v-if="hotelsStore.isLoading" class="text-center pa-5"><v-progress-circular indeterminate color="#ff7b00"></v-progress-circular></div>
                      <div v-else-if="hotelsStore.data && hotelsStore.data.length > 0">
                        <v-card v-for="(hotel, i) in hotelsStore.data" :key="i" class="mb-4 pa-5 rounded-lg flight-hotel-card text-white" elevation="0">
                          <div class="d-flex justify-space-between align-center">
                            <div>
                              <div class="font-weight-bold text-body-1">{{ hotel.name }}</div>
                              <div class="text-caption text-amber mt-1">
                                <v-icon size="x-small" class="mr-1">mdi-star</v-icon> {{ hotel.rating }}/10
                              </div>
                            </div>
                            <div class="text-h6 font-weight-black">{{ Math.round(hotel.price) }} <span class="text-caption">PLN</span></div>
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
                    <v-card class="d-flex flex-column rounded-xl glass-card text-white border-0" height="600">
                      <v-card-title class="pa-5 border-b border-opacity-25 d-flex align-center">
                        <v-icon left color="#ff7b00" class="mr-2">mdi-chat</v-icon> Twój Przewodnik AI
                      </v-card-title>

                      <div class="flex-grow-1 overflow-y-auto pa-5" id="chat-container">
                        <div v-for="(msg, i) in chatMessages" :key="i" :class="msg.role === 'user' ? 'text-right' : 'text-left'" class="mb-4">
                          <v-sheet :color="msg.role === 'user' ? '#ff7b00' : 'rgba(255,255,255,0.1)'" class="text-white pa-4 d-inline-block text-body-1" :rounded="msg.role === 'user' ? 'xl xl-0 xl xl' : 'xl xl xl xl-0'" style="max-width: 85%;">
                            {{ msg.text }}
                          </v-sheet>
                        </div>
                        <div v-if="chatLoading" class="text-left mb-4">
                          <v-sheet color="rgba(255,255,255,0.1)" rounded="xl xl xl xl-0" class="pa-4 d-inline-block text-white">
                            <v-progress-circular indeterminate size="16" color="#ff7b00" class="mr-2"></v-progress-circular> Pisze...
                          </v-sheet>
                        </div>
                      </div>

                      <div class="pa-4 border-t border-opacity-25">
                        <v-text-field v-model="chatInput" placeholder="Napisz do asystenta..." variant="solo" density="comfortable" hide-details @keyup.enter="sendChatMessage" rounded="pill" bg-color="rgba(255,255,255,0.1)" class="text-white">
                          <template v-slot:append-inner>
                            <v-btn icon="mdi-send" color="#ff7b00" variant="text" @click="sendChatMessage" :disabled="!chatInput.trim()"></v-btn>
                          </template>
                        </v-text-field>
                      </div>
                    </v-card>
                  </v-col>

                  <v-col cols="12" md="4">
                    <v-card class="pa-6 rounded-xl glass-card text-white h-100 border-0" elevation="0">
                      <h2 class="text-h5 font-weight-bold mb-6 text-center d-flex justify-center align-center">
                        <v-icon color="amber" class="mr-2">mdi-weather-partly-cloudy</v-icon> Pogoda
                      </h2>
                      <div v-if="weatherStore.isLoading" class="text-center pa-5"><v-progress-circular indeterminate color="amber"></v-progress-circular></div>
                      <div v-else class="d-flex flex-column gap-3">
                        <div v-for="(day, index) in weatherStore.data.slice(0,5)" :key="index" class="pa-4 text-center rounded-lg weather-card d-flex align-center justify-space-between">
                          <div class="font-weight-bold text-caption text-grey-lighten-1">{{ day.date }}</div>
                          <div class="d-flex align-center">
                            <div class="text-h5 mr-3">{{ day.icon }}</div>
                            <div class="text-h6 font-weight-black">{{ Math.round(day.temperature) }}°C</div>
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

      <div class="right-panel form-panel pl-10 pr-10 pt-16 pb-10">

        <div class="mb-12">
          <h2 class="text-h4 font-weight-bold text-white mb-2">Zaplanuj Lot</h2>
          <p class="text-grey-lighten-1 text-subtitle-2">Szybko, prosto i z asystą AI.</p>
        </div>

        <div class="d-flex flex-column gap-6 mb-8 flex-grow-1">
          <v-autocomplete v-model="selectedOrigin" :items="polishAirports" item-title="name" item-value="code"
            label="Skąd wylatujesz?" variant="underlined" prepend-inner-icon="mdi-map-marker" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-autocomplete>

          <v-autocomplete v-model="selectedDestination" :items="popularDestinations" item-title="en" return-object
            label="Gdzie lecisz?" variant="underlined" prepend-inner-icon="mdi-airplane-landing" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-autocomplete>

          <v-text-field v-model="startDate" label="Data wylotu" type="date" variant="underlined" prepend-inner-icon="mdi-calendar" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-text-field>

          <v-text-field v-model.number="days" label="Czas trwania (dni)" type="number" min="1" max="30" variant="underlined" prepend-inner-icon="mdi-clock-outline" base-color="grey-darken-1" color="#ff7b00" theme="dark" hide-details class="custom-input"></v-text-field>
        </div>

        <v-btn color="#ff7b00" size="x-large" block rounded="pill" class="mt-auto font-weight-bold text-white mb-4 custom-shadow hover-scale" elevation="8" @click="generateTrip" :loading="isSearching">
          Wyszukaj <v-icon right size="small" class="ml-2">mdi-chevron-right</v-icon>
        </v-btn>
      </div>
    </div>
  </v-app>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { useWeatherStore } from '../core/weather'
import { useFlightsStore } from '../core/flights'
import { useHotelsStore } from '../core/hotels'

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

body, .v-application {
  font-family: 'Inter', sans-serif !important;
}

/* GŁÓWNY GRID PODZIAŁU */
.split-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  background-color: #0f1319; /* Ciemne tło dla całej aplikacji podczas wyników */
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
}

.results-bg {
  background: #121822 !important; /* Jednolite ciemne tło pod panelem wyników */
}

/* PRAWY PANEL (FORMULARZ BOCZNY) */
.form-panel {
  width: 440px;
  background: linear-gradient(160deg, #37475c 0%, #222d3d 100%);
  display: flex;
  flex-direction: column;
  z-index: 10;
  box-shadow: -15px 0 40px rgba(0,0,0,0.3);
}

/* Glassmorphism dla paneli wyników (Loty, AI, Hotele) */
.glass-card {
  background: rgba(255, 255, 255, 0.03) !important;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.flight-hotel-card, .weather-card {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.05) !important;
  transition: background 0.2s ease;
}
.flight-hotel-card:hover { background: rgba(255, 255, 255, 0.1) !important; }

/* TYPOGRAFIA OZDOBNA */
.script-title {
  font-family: 'Playball', cursive;
  font-size: 8rem;
  line-height: 1;
  text-shadow: 2px 4px 15px rgba(0,0,0,0.3);
}

/* ZMIANY VUETIFY */
.custom-input .v-field__input { font-size: 1.1rem; padding-top: 10px; padding-bottom: 5px; }
.custom-shadow { box-shadow: 0 10px 25px rgba(255, 123, 0, 0.4) !important; }
.hover-scale { transition: transform 0.2s; }
.hover-scale:hover { transform: scale(1.02); }
.gap-6 { gap: 24px; }
.gap-8 { gap: 32px; }

/* AI KONTENT STYL */
.ai-content h1, .ai-content h2, .ai-content h3 { color: #ff7b00; margin-top: 20px; margin-bottom: 10px; font-weight: 600; }
.ai-content p { margin-bottom: 12px; line-height: 1.6; }
.ai-content ul { padding-left: 20px; margin-bottom: 20px; }
.ai-content li { margin-bottom: 8px; }

/* MAGICZNY TRYB CIEMNY DLA MAPY OPENLAYERS */
.dark-map {
  filter: invert(100%) hue-rotate(180deg) brightness(85%) contrast(90%);
}

/* ZAKŁADKI */
.v-tab { text-transform: none !important; font-weight: 500; letter-spacing: 0.5px; font-size: 1rem; }
.v-slide-group__content { padding-bottom: 2px; }

@media (max-width: 960px) {
  .split-layout { flex-direction: column; height: auto; min-height: 100vh; overflow-y: auto; }
  .left-panel { height: 100vh; flex: none; }
  .form-panel { width: 100%; height: auto; }
  .script-title { font-size: 5rem; }
}

/* Paski przewijania (Scrollbar) dla ciemnego UI */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.1); }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.4); }
</style>