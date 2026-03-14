import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface HotelData {
  name: string;
  rating: number;
  price: number;
  currency: string;
}

export const useHotelsStore = defineStore('hotels', () => {
  const data = ref<HotelData[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const fetchHotels = async (city: string, checkIn: string, checkOut: string) => {
    isLoading.value = true
    error.value = null
    data.value = []

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/hotels?city=${city}&check_in=${checkIn}&check_out=${checkOut}`)
      if (!response.ok) throw new Error('Nie udało się pobrać hoteli.')

      const result = await response.json()
      data.value = result.data
    } catch (err: any) {
      error.value = err.message || 'Błąd serwera.'
    } finally {
      isLoading.value = false
    }
  }

  return { data, isLoading, error, fetchHotels }
})