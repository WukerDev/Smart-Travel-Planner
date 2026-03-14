import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface WeatherData {
  city: string;
  temperature: number;
  description: string;
  humidity: number;
  wind_speed: number;
}

export const useWeatherStore = defineStore('weather', () => {
  const data = ref<WeatherData | null>(null)
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const fetchWeather = async (city: string) => {
    isLoading.value = true
    error.value = null
    data.value = null

    try {
      const response = await fetch(`http://127.0.0.1:8000/api/weather/${city}`)

      if (!response.ok) {
        throw new Error('Nie udało się pobrać pogody. Sprawdź nazwę miasta.')
      }
      data.value = await response.json()
    } catch (err: any) {
      error.value = err.message || 'Błąd połączenia z serwerem.'
    } finally {
      isLoading.value = false
    }
  }

  return { data, isLoading, error, fetchWeather }
})