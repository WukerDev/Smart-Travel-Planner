import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useExtrasStore = defineStore('extras', () => {
  const events = ref<any[]>([])
  const pois = ref<any[]>([])
  const isLoading = ref(false)

  const fetchExtras = async (cityEn: string, lat: number, lon: number, startDate: string, checkOutDate: string) => {
    isLoading.value = true
    events.value = []
    pois.value = []

    try {
      const evRes = await fetch(`http://127.0.0.1:8000/api/events?city=${cityEn}&start_date=${startDate}&end_date=${checkOutDate}`)
      const evData = await evRes.json()
      if (evData && evData.data) events.value = evData.data
    } catch(e) {}

    try {
      const poiRes = await fetch(`http://127.0.0.1:8000/api/pois?lat=${lat}&lon=${lon}`)
      const poiData = await poiRes.json()
      if (poiData && poiData.data) pois.value = poiData.data
    } catch(e) {}

    isLoading.value = false
  }

  return { events, pois, isLoading, fetchExtras }
})