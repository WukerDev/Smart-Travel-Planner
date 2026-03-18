import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAiStore = defineStore('ai', () => {
  const itineraryContent = ref('')
  const isItineraryLoading = ref(false)
  const chatMessages = ref<{role: string, text: string}[]>([])
  const isChatLoading = ref(false)

  const generateItinerary = async (cityEn: string, days: number, lang: string = 'pl') => {
    isItineraryLoading.value = true
    itineraryContent.value = ''
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/itinerary?city=${cityEn}&days=${days}&lang=${lang}`)
      const json = await res.json()
      itineraryContent.value = json.data.replace(/```html/g, '').replace(/```/g, '')
    } catch (e) {
      itineraryContent.value = "<h3 class='text-error'>Błąd generowania. Serwer Ollama wyłączony?</h3>"
    } finally {
      isItineraryLoading.value = false
    }
  }

  const resetChat = (cityPl: string, lang: string = 'pl') => {
    const greeting = lang === 'en'
      ? `Hi! Ready for a trip to ${cityPl}? How can I help you?`
      : `Cześć! Gotowy na podróż do ${cityPl}? W czym mogę pomóc?`

    chatMessages.value = [
      { role: 'ai', text: greeting }
    ]
  }

const sendMessage = async (userMsg: string, cityPl: string, lang: string = 'pl') => {
    if (!userMsg.trim()) return

    chatMessages.value.push({ role: 'user', text: userMsg })
    isChatLoading.value = true

    try {
      const res = await fetch('http://127.0.0.1:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, city: cityPl, lang })
      })
      const data = await res.json()
      chatMessages.value.push({ role: 'ai', text: data.reply })
    } catch (e) {
      chatMessages.value.push({ role: 'ai', text: 'Błąd połączenia z serwerem Ollama.' })
    } finally {
      isChatLoading.value = false
    }
  }
  return { itineraryContent, isItineraryLoading, chatMessages, isChatLoading, generateItinerary, resetChat, sendMessage }
})