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

const fetchWeather = async (city: string, startDate: string, days: number, lang: string = 'pl') => {
    isLoading.value = true
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/weather/${city}?start_date=${startDate}&days=${days}&lang=${lang}`)
      const json = await res.json()
      data.value = json.data
    } catch (e) {
      data.value = []
    } finally {
      isLoading.value = false
    }
  }

  return { data, city, isLoading, error, fetchWeather }
})