import { useEffect, useState } from 'react'
import * as api from './api'
import Board from './components/Board'
import CardModal from './components/CardModal'
import SummaryBar from './components/SummaryBar'
import './App.css'

export default function App() {
  const [columns, setColumns] = useState([])
  const [cards, setCards] = useState([])
  const [loading, setLoading] = useState(true)
  // { mode: 'create', column } | { mode: 'edit', card } | null
  const [modal, setModal] = useState(null)

  useEffect(() => {
    api.getBoard().then(({ columns, cards }) => {
      setColumns(columns)
      setCards(cards)
      setLoading(false)
    })
  }, [])

  function handleDragEnd(event) {
    const { active, over } = event
    if (!over) return
    const cardId = active.id
    const targetColumn = over.id
    const card = cards.find((c) => c.id === cardId)
    if (!card || card.column === targetColumn) return

    setCards((prev) => prev.map((c) => (c.id === cardId ? { ...c, column: targetColumn } : c)))
    api.moveCard(cardId, { column: targetColumn })
  }

  function handleAddCard(columnId) {
    setModal({ mode: 'create', column: columnId })
  }

  function handleEditCard(card) {
    setModal({ mode: 'edit', card })
  }

  async function handleDeleteCard(cardId) {
    setCards((prev) => prev.filter((c) => c.id !== cardId))
    await api.deleteCard(cardId)
  }

  async function handleSaveModal({ title, description }) {
    if (modal.mode === 'create') {
      const created = await api.createCard({ title, description, column: modal.column })
      setCards((prev) => [...prev, created])
    } else {
      const updated = await api.updateCard(modal.card.id, { title, description })
      setCards((prev) => prev.map((c) => (c.id === updated.id ? updated : c)))
    }
    setModal(null)
  }

  if (loading) {
    return <p className="loading">Loading board…</p>
  }

  return (
    <div className="app">
      <header className="app__header">
        <h1>Boardly</h1>
      </header>

      <SummaryBar columns={columns} cards={cards} />

      <Board
        columns={columns}
        cards={cards}
        onDragEnd={handleDragEnd}
        onAddCard={handleAddCard}
        onEditCard={handleEditCard}
        onDeleteCard={handleDeleteCard}
      />

      {modal && (
        <CardModal
          initialTitle={modal.mode === 'edit' ? modal.card.title : ''}
          initialDescription={modal.mode === 'edit' ? modal.card.description : ''}
          onSave={handleSaveModal}
          onCancel={() => setModal(null)}
        />
      )}
    </div>
  )
}
