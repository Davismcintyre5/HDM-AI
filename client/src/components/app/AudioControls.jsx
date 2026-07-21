import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';

export default function AudioControls({ onTranscript, onSpeakingChange, language = 'en' }) {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);

  useEffect(() => {
    setSpeechSupported(
      'SpeechRecognition' in window || 'webkitSpeechRecognition' in window
    );
    synthRef.current = window.speechSynthesis;
  }, []);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) return;

    const recognition = new SpeechRecognition();
    recognition.lang = language;
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (onTranscript) onTranscript(transcript);
    };

    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognitionRef.current = recognition;
    recognition.start();
    setIsListening(true);
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const toggleListening = () => {
    if (isListening) stopListening();
    else startListening();
  };

  const speak = (text, lang = language) => {
    if (!synthRef.current) return;

    synthRef.current.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = 0.9;
    utterance.pitch = 1.1;

    utterance.onstart = () => {
      setIsSpeaking(true);
      if (onSpeakingChange) onSpeakingChange(true);
    };
    utterance.onend = () => {
      setIsSpeaking(false);
      if (onSpeakingChange) onSpeakingChange(false);
    };
    utterance.onerror = () => {
      setIsSpeaking(false);
      if (onSpeakingChange) onSpeakingChange(false);
    };

    synthRef.current.speak(utterance);
  };

  const stopSpeaking = () => {
    if (synthRef.current) {
      synthRef.current.cancel();
      setIsSpeaking(false);
      if (onSpeakingChange) onSpeakingChange(false);
    }
  };

  return { isListening, isSpeaking, toggleListening, speak, stopSpeaking, speechSupported };
}