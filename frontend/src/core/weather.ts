import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface DailyWeather {
  date: string;
  temperature: number;
  description: string;
  icon: string;
}

export const useWeatherStore = defineStore('weather', () => {
  const data = ref<DailyWeather[]>([])
  const city = ref<string>('')
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const fetchWeather = async (cityName: string, startDate: string, days: number) => {
    isLoading.value = true
    error.value = null
    data.value = []

    try {
      // Uderzamy do FastAPI z nowymi parametrami daty i dni!
      const response = await fetch(`http://127.0.0.1:8000/api/weather/${cityName}?start_date=${startDate}&days=${days}`)
      if (!response.ok) throw new Error('Nie udało się pobrać pogody.')

      const result = await response.json()
      data.value = result.data
      city.value = result.city
    } catch (err: any) {
      error.value = err.message || 'Błąd serwera.'
    } finally {
      isLoading.value = false
    }
  }

  return { data, city, isLoading, error, fetchWeather }
})