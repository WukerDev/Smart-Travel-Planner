import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWeatherStore = defineStore('weather', () => {
  // Stan (State)
  const temperature = ref(22)
  const city = ref('Bydgoszcz')

  // Akcje (Actions)
  function setCity(newCity) {
    city.value = newCity
  }

  return { temperature, city, setCity }
})