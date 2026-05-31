import { createContext, useContext, useState, useEffect } from 'react'

const ContextoTema = createContext()

export function ContextoTemaProvider({ children }) {
  const [oscuro, setOscuro] = useState(() => {
    const guardado = localStorage.getItem('tema')
    if (guardado) return guardado === 'oscuro'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    if (oscuro) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
    localStorage.setItem('tema', oscuro ? 'oscuro' : 'claro')
  }, [oscuro])

  const toggleTema = () => setOscuro(prev => !prev)

  return (
    <ContextoTema.Provider value={{ oscuro, toggleTema }}>
      {children}
    </ContextoTema.Provider>
  )
}

export const useTema = () => useContext(ContextoTema)
export default ContextoTema
