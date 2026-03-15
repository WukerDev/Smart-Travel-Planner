<template>
  <v-container class="mt-5" fluid>

    <div class="d-flex justify-end mb-4">
      <v-btn
        :icon="isDark ? 'mdi-weather-sunny' : 'mdi-weather-night'"
        :color="isDark ? 'amber' : 'indigo'"
        variant="tonal"
        elevation="2"
        @click="toggleTheme"
        class="transition-swing"
      ></v-btn>
    </div>

    <v-card class="pa-8 mx-auto mb-8 hero-card" max-width="1200" elevation="4" rounded="xl" border>
      <div class="text-center mb-8">
        <v-avatar :color="isDark ? 'grey-darken-3' : 'primary-lighten-4'" size="70" class="mb-4 elevation-2">
          <v-icon size="40" color="primary">mdi-airplane-takeoff</v-icon>
        </v-avatar>
        <h1 class="text-h3 text-primary font-weight-black mb-2">Smart Travel Planner</h1>
        <p class="text-subtitle-1 text-medium-emphasis">Zintegrowane AI, Mapy, Wydarzenia na żywo i Lokalny Asystent.</p>
      </div>

      <v-row>
        <v-col cols="12" md="3">
          <v-autocomplete v-model="selectedOrigin" :items="polishAirports" item-title="name" item-value="code"
            label="Skąd wylatujesz?" variant="outlined" prepend-inner-icon="mdi-map-marker-outline" color="primary" hide-details="auto" bg-color="surface"></v-autocomplete>
        </v-col>
        <v-col cols="12" md="3">
          <v-autocomplete v-model="selectedDestination" :items="popularDestinations" item-title="pl" return-object
            label="Gdzie lecisz?" variant="outlined" prepend-inner-icon="mdi-earth" color="primary" hide-details="auto" bg-color="surface"></v-autocomplete>
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field v-model="startDate" label="Data wyjazdu" type="date" variant="outlined" prepend-inner-icon="mdi-calendar" color="primary" hide-details="auto" bg-color="surface"></v-text-field>
        </v-col>
        <v-col cols="12" md="3">
          <v-text-field v-model.number="days" label="Liczba dni pobytu" type="number" min="1" max="30" variant="outlined" prepend-inner-icon="mdi-weather-night" color="primary" hide-details="auto" bg-color="surface"></v-text-field>
        </v-col>
      </v-row>

      <v-btn color="primary" size="x-large" block rounded="lg" class="mt-8 text-body-1 font-weight-bold" elevation="4" :loading="isSearching" @click="generateTrip">
        <v-icon left class="mr-2">mdi-magic-staff</v-icon> Zaplanuj moją podróż
      </v-btn>
    </v-card>

    <v-fade-transition>
      <div v-if="showResults">
        <v-row>

          <v-col cols="12" md="3" style="align-self: flex-start;" class="sticky-sidebar">
            <v-card color="primary" class="pa-5" elevation="4" rounded="xl">
              <h2 class="text-h5 font-weight-bold mb-4 text-center text-white">
                Pogoda: <br><span class="text-amber-lighten-2">{{ weatherStore.city }}</span>
              </h2>
              <div v-if="weatherStore.isLoading" class="text-center pa-5"><v-progress-circular indeterminate color="white"></v-progress-circular></div>
              <div v-else class="d-flex flex-column gap-3">
                <v-card v-for="(day, index) in weatherStore.data" :key="index" class="pa-3 text-center" color="surface" rounded="lg" elevation="2">
                  <div class="font-weight-bold text-primary">{{ day.date }}</div>
                  <div class="text-h4 my-1">{{ day.icon }}</div>
                  <div class="text-h6 font-weight-black text-high-emphasis">{{ Math.round(day.temperature) }}°C</div>
                  <div class="text-caption text-medium-emphasis text-uppercase">{{ day.description }}</div>
                </v-card>
              </div>
            </v-card>
          </v-col>

          <v-col cols="12" md="6">

            <v-card class="mb-6 overflow-hidden" elevation="4" rounded="xl" border>
              <div class="bg-surface-variant pa-3 text-center font-weight-bold text-high-emphasis border-b">
                <v-icon class="mr-2">mdi-map</v-icon> Trasa Twojego lotu i Atrakcje
              </div>
              <div ref="mapContainer" :class="{'dark-map': isDark}" style="height: 350px; width: 100%;"></div>
            </v-card>

            <v-card class="mb-6 pa-6" elevation="4" rounded="xl" border>
              <div class="d-flex align-center mb-4">
                <v-icon color="secondary" size="30" class="mr-3">mdi-sparkles</v-icon>
                <h3 class="text-h5 font-weight-bold text-high-emphasis">Twój Plan Wycieczki (AI)</h3>
              </div>
              <v-divider class="mb-4"></v-divider>

              <div v-if="aiLoading" class="text-center pa-8">
                <v-progress-circular indeterminate color="secondary" size="50"></v-progress-circular>
                <div class="mt-4 text-medium-emphasis font-weight-medium">Llama 3.1 generuje plan specjalnie dla Ciebie...</div>
              </div>
              <div v-else v-html="aiContent" class="ai-content text-body-1 text-medium-emphasis"></div>
            </v-card>

            <v-card class="pa-5 mb-6" elevation="4" rounded="xl" border>
              <div class="d-flex align-center mb-4">
                <v-icon color="orange-darken-2" size="30" class="mr-3">mdi-ticket-confirmation</v-icon>
                <h3 class="text-h5 font-weight-bold text-high-emphasis">Wydarzenia w {{ selectedDestination.pl }}</h3>
              </div>

              <v-row v-if="events.length > 0">
                <v-col v-for="(event, i) in events" :key="i" cols="12" sm="6">
                  <v-card variant="outlined" rounded="lg" hover :href="event.url" target="_blank" class="h-100 d-flex flex-column border-opacity-50">
                    <v-img :src="event.image" height="120" cover v-if="event.image"></v-img>
                    <v-card-text class="pa-3 flex-grow-1 bg-surface">
                      <div class="text-subtitle-2 font-weight-bold text-high-emphasis" style="line-height: 1.2;">{{ event.name }}</div>
                      <div class="text-caption text-primary mt-2 font-weight-bold">
                        <v-icon size="small" class="mr-1">mdi-calendar</v-icon>{{ event.date }}
                      </div>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
              <div v-else class="text-center pa-5">
                <v-progress-circular indeterminate color="orange" v-if="isSearchingExtras"></v-progress-circular>
                <span v-else class="text-medium-emphasis">Szukamy ciekawych wydarzeń w tym terminie...</span>
              </div>
            </v-card>

            <v-card class="pa-5 mb-6" elevation="4" rounded="xl" border>
              <div class="d-flex align-center mb-6">
                <v-icon size="30" color="secondary" class="mr-3">mdi-airplane</v-icon>
                <h3 class="text-h5 font-weight-bold text-high-emphasis">Najtańsze Loty</h3>
              </div>
              <div v-if="flightsStore.isLoading" class="text-center pa-10"><v-progress-circular indeterminate color="primary"></v-progress-circular></div>
              <v-alert v-else-if="flightsStore.error" type="error" variant="tonal" rounded="lg">{{ flightsStore.error }}</v-alert>
              <div v-else-if="flightsStore.data && flightsStore.data.length > 0">
                <v-card v-for="(flight, i) in flightsStore.data" :key="i" class="mb-4 pa-4 transition-swing border-opacity-50" variant="outlined" rounded="lg" hover color="surface">
                  <div class="d-flex justify-space-between align-center">
                    <div>
                      <div class="text-h6 font-weight-bold text-primary">{{ flight.airline }}</div>
                      <div class="text-subtitle-2 text-medium-emphasis mt-1">
                        <v-icon size="small" class="mr-1">mdi-clock-outline</v-icon>
                        {{ flight.departure_time }} ➔ {{ flight.arrival_time }}
                      </div>
                    </div>
                    <div class="text-h5 text-green-darken-2 font-weight-black">{{ Math.round(flight.price) }} <span class="text-body-2">PLN</span></div>
                  </div>
                </v-card>
              </div>
              <v-alert v-else type="info" variant="tonal" rounded="lg">Brak lotów w tym terminie.</v-alert>
            </v-card>

            <v-card class="pa-5 mb-6" elevation="4" rounded="xl" border>
              <div class="d-flex align-center mb-6">
                <v-icon size="30" color="secondary" class="mr-3">mdi-bed</v-icon>
                <h3 class="text-h5 font-weight-bold text-high-emphasis">Polecane Hotele</h3>
              </div>
              <div v-if="hotelsStore.isLoading" class="text-center pa-10"><v-progress-circular indeterminate color="primary"></v-progress-circular></div>
              <v-alert v-else-if="hotelsStore.error" type="error" variant="tonal" rounded="lg">{{ hotelsStore.error }}</v-alert>
              <div v-else-if="hotelsStore.data && hotelsStore.data.length > 0">
                <v-card v-for="(hotel, i) in hotelsStore.data" :key="i" class="mb-4 pa-4 transition-swing border-opacity-50" variant="outlined" rounded="lg" hover color="surface">
                  <div class="d-flex justify-space-between align-center">
                    <div class="pr-3">
                      <div class="text-h6 font-weight-bold text-primary" style="line-height: 1.2;">{{ hotel.name }}</div>
                      <div class="text-subtitle-2 text-amber-darken-2 mt-2 font-weight-bold">
                        <v-icon size="small" class="mr-1">mdi-star</v-icon> Ocena: {{ hotel.rating }}/10
                      </div>
                    </div>
                    <div class="text-right">
                      <div class="text-h5 text-primary font-weight-black">{{ Math.round(hotel.price) }} <span class="text-body-2">PLN</span></div>
                    </div>
                  </div>
                </v-card>
              </div>
              <v-alert v-else type="info" variant="tonal" rounded="lg">Brak hoteli w tym terminie.</v-alert>
            </v-card>

          </v-col>

          <v-col cols="12" md="3" style="align-self: flex-start;" class="sticky-sidebar">
            <v-card class="d-flex flex-column" elevation="6" rounded="xl" border style="height: 80vh; max-height: 800px;">
              <v-card-title class="bg-primary text-white pa-4 d-flex align-center">
                <v-icon class="mr-2">mdi-chat-processing-outline</v-icon>
                Lokalny Czat (Llama 3)
              </v-card-title>
              <v-divider></v-divider>

              <div class="flex-grow-1 overflow-y-auto pa-4 bg-background" id="chat-container">
                <div v-for="(msg, i) in chatMessages" :key="i" :class="msg.role === 'user' ? 'text-right' : 'text-left'" class="mb-4">
                  <v-sheet
                    :color="msg.role === 'user' ? 'primary' : 'surface'"
                    :class="msg.role === 'user' ? 'text-white' : 'text-high-emphasis'"
                    elevation="2"
                    rounded="xl"
                    class="pa-4 d-inline-block text-body-1 text-left border"
                    style="white-space: pre-wrap; max-width: 90%; line-height: 1.5;"
                  >
                    {{ msg.text }}
                  </v-sheet>
                </div>

                <div v-if="chatLoading" class="text-left mb-4">
                  <v-sheet color="surface" elevation="2" rounded="xl" class="pa-4 d-inline-block border">
                    <div class="d-flex align-center">
                      <v-progress-circular indeterminate size="20" color="primary"></v-progress-circular>
                      <span class="ml-3 text-medium-emphasis font-weight-medium">Llama 3.1 pisze...</span>
                    </div>
                  </v-sheet>
                </div>
              </div>

              <div class="pa-3 bg-surface border-t">
                <v-text-field
                  v-model="chatInput"
                  placeholder="Zapytaj o wskazówki..."
                  variant="outlined"
                  density="compact"
                  hide-details
                  @keyup.enter="sendChatMessage"
                  rounded="lg"
                  bg-color="background"
                >
                  <template v-slot:append-inner>
                    <v-btn icon="mdi-send" color="primary" variant="text" size="small" @click="sendChatMessage" :loading="chatLoading" :disabled="!chatInput.trim()"></v-btn>
                  </template>
                </v-text-field>
              </div>
            </v-card>
          </v-col>

        </v-row>
      </div>
    </v-fade-transition>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue'
import { useTheme } from 'vuetify' // Dodano obsługę motywów
import { useWeatherStore } from '../core/weather'
import { useFlightsStore } from '../core/flights'
import { useHotelsStore } from '../core/hotels'

// IMPORTY OPENLAYERS
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

// LOGIKA MOTYWÓW VUETIFY
const theme = useTheme()
const toggleTheme = () => {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
}
const isDark = computed(() => theme.global.current.value.dark)

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

// ZMIENNE AI PLANU (Llama)
const aiContent = ref('')
const aiLoading = ref(false)

// ZMIENNE WYDARZEŃ
const events = ref<any[]>([])
const isSearchingExtras = ref(false)

// ZMIENNE CZATU (Ollama)
const chatInput = ref('')
const chatLoading = ref(false)
const chatMessages = ref<{role: string, text: string}[]>([])

// ZMIENNE DO MAPY
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
    console.error('Błąd ładowania słowników z bazy:', error)
  }
})

const isSearching = computed(() => {
  return weatherStore.isLoading || flightsStore.isLoading || hotelsStore.isLoading
})

const calculateCheckOutDate = (startDate: string, days: number) => {
  const date = new Date(startDate)
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

// ==========================================
// FUNKCJE AI (Generowanie Planu i Czat)
// ==========================================

const generateAiItinerary = async () => {
  aiLoading.value = true
  aiContent.value = ''
  try {
    const res = await fetch(`http://127.0.0.1:8000/api/itinerary?city=${selectedDestination.value.en}&days=${days.value}`)
    const json = await res.json()
    let cleanHtml = json.data.replace(/```html/g, '').replace(/```/g, '')
    aiContent.value = cleanHtml
  } catch (e) {
    aiContent.value = "<h3 class='text-error'>Wystąpił błąd podczas generowania planu z Ollamy.</h3>"
  } finally {
    aiLoading.value = false
  }
}

const sendChatMessage = async () => {
  if (!chatInput.value.trim() || chatLoading.value) return

  const userMsg = chatInput.value
  chatMessages.value.push({ role: 'user', text: userMsg })
  chatInput.value = ''
  chatLoading.value = true

  scrollToBottomChat()

  try {
    const res = await fetch('http://127.0.0.1:8000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMsg, city: selectedDestination.value.pl })
    })
    const data = await res.json()
    chatMessages.value.push({ role: 'ai', text: data.reply })
  } catch (e) {
    chatMessages.value.push({ role: 'ai', text: 'Wystąpił błąd połączenia z serwerem Ollama.' })
  } finally {
    chatLoading.value = false
    scrollToBottomChat()
  }
}

const scrollToBottomChat = () => {
  setTimeout(() => {
    const box = document.getElementById('chat-container')
    if (box) box.scrollTop = box.scrollHeight
  }, 100)
}

// ==========================================
// WYDARZENIA, POI ORAZ MAPY
// ==========================================

const fetchExtras = async () => {
  isSearchingExtras.value = true
  events.value = []
  const checkOutDate = calculateCheckOutDate(startDate.value, days.value)

  try {
    const evRes = await fetch(`http://127.0.0.1:8000/api/events?city=${selectedDestination.value.en}&start_date=${startDate.value}&end_date=${checkOutDate}`)
    const evData = await evRes.json()
    events.value = evData.data || []
  } catch(e) { console.error("Błąd pobierania wydarzeń", e) }

  try {
    const poiRes = await fetch(`http://127.0.0.1:8000/api/pois?lat=${selectedDestination.value.lat}&lon=${selectedDestination.value.lon}`)
    const poiData = await poiRes.json()
    addPoisToMap(poiData.data || [])
  } catch(e) { console.error("Błąd pobierania POI", e) }

  isSearchingExtras.value = false
}

const addPoisToMap = (pois: any[]) => {
  if (!vectorLayer) return
  const source = vectorLayer.getSource()
  if (!source) return

  const poiIcon = `data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath fill='%232196F3' d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E`;

  pois.forEach(poi => {
    if(!poi.lon || !poi.lat) return
    const feature = new Feature({ geometry: new Point(fromLonLat([poi.lon, poi.lat])) })
    feature.setStyle(new Style({ image: new Icon({ src: poiIcon, anchor: [0.5, 1], scale: 0.8 }) }))
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
  await nextTick()
  if (!mapContainer.value) return

  if (!olMap) {
    vectorLayer = new VectorLayer({ source: new VectorSource() })
    olMap = new Map({
      target: mapContainer.value,
      layers: [
        new TileLayer({ source: new OSM() }),
        vectorLayer
      ],
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
    // Rysujemy linię reagującą na motyw (jasny błękit dla dark mode, mocny niebieski dla light)
    flightLine.setStyle(new Style({ stroke: new Stroke({ color: isDark.value ? '#64B5F6' : '#1E88E5', width: 3 }) }))
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

const generateTrip = async () => {
  if (!selectedOrigin.value || !selectedDestination.value || !days.value) return

  showResults.value = true

  chatMessages.value = [
    { role: 'ai', text: `Cześć! Jestem Twoim lokalnym asystentem. Gotowy na podróż do miasta ${selectedDestination.value.pl}? W czym mogę pomóc?` }
  ]

  const checkOutDate = calculateCheckOutDate(startDate.value, days.value)

  weatherStore.fetchWeather(selectedDestination.value.en, startDate.value, days.value)
  flightsStore.fetchFlights(selectedOrigin.value, selectedDestination.value.airport, startDate.value)
  hotelsStore.fetchHotels(selectedDestination.value.en, startDate.value, checkOutDate)

  await drawMap()
  fetchExtras()
  generateAiItinerary()
}
</script>

<style>
/* GŁÓWNY PRZEŁĄCZNIK TRYBÓW */
html {
  transition: background-color 0.3s ease;
}

/* Klasa odpowiedzialna za przyklejenie kolumn bocznych przy scrollowaniu */
.sticky-sidebar {
  position: sticky;
  top: 20px;
}

/* MAGICZNY TRYB CIEMNY DLA MAPY OPENLAYERS */
.dark-map {
  filter: invert(90%) hue-rotate(180deg) brightness(95%) contrast(85%);
  transition: filter 0.5s ease;
}

/* AI HTML Formatter - Podpięty pod zmienne Vuetify */
.ai-content h1, .ai-content h2, .ai-content h3 {
  color: rgb(var(--v-theme-primary));
  margin-top: 15px;
  margin-bottom: 8px;
}
.ai-content p { margin-bottom: 10px; line-height: 1.6; }
.ai-content ul { padding-left: 20px; margin-bottom: 15px; }
.ai-content li { margin-bottom: 5px; }

.gap-3 { gap: 12px; }

/* Subtelne przejścia na hover i komponentach */
.transition-swing {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.5, 1);
}
</style>