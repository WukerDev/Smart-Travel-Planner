import { defineStore } from 'pinia'
import { ref } from 'vue'
export interface FlightData {
  id: string;
  airline: string;
  departure_time: string;
  arrival_time: string;
  price: number;
}

export const useFlightsStore = defineStore('flights', () => {
  const data = ref<FlightData[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const fetchFlights = async (origin: string, destination: string, date: string) => {
    isLoading.value = true
    error.value = null
    data.value = []

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/flights?origin=${origin}&destination=${destination}&date=${date}`)

      if (!response.ok) {
        throw new Error('Nie udało się pobrać lotów. Sprawdź kody lotnisk.')
      }
      const result = await response.json()
      data.value = result.data || result
    } catch (err: any) {
      error.value = err.message || 'Błąd połączenia z serwerem.'
    } finally {
      isLoading.value = false
    }
  }

  return { data, isLoading, error, fetchFlights }
})