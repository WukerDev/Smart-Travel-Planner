import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLocationsStore = defineStore('locations', () => {
  const airports = ref<any[]>([])
  const destinations = ref<any[]>([])

  const fetchLocations = async () => {
    try {
      const [airportsRes, destRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/airports'),
        fetch('http://127.0.0.1:8000/api/destinations')
      ])
      airports.value = await airportsRes.json()
      destinations.value = await destRes.json()
    } catch (error) {}
  }

  return { airports, destinations, fetchLocations }
})