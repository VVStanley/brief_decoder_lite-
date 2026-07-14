import { useState } from 'react';
import styles from './ParserForm.module.css';

interface ParserFormProps {
  onSubmit: (text: string) => void;
  isLoading: boolean;
}

export function ParserForm({ onSubmit, isLoading }: ParserFormProps) {
  const [text, setText] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim().length >= 10) {
      onSubmit(text);
    }
  };

  const handleImportText = async () => {
    if (typeof chrome !== 'undefined' && chrome.tabs) {
      try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab?.id) {
          // Send message to content script of the active tab to get selection
          chrome.tabs.sendMessage(
            tab.id,
            { action: 'GET_SELECTED_TEXT' },
            (response: { text: string } | undefined) => {
              if (chrome.runtime.lastError) {
                console.warn('Вкладка еще не загрузилась или на ней запрещены скрипты:', chrome.runtime.lastError.message);
                return;
              }
              if (response && response.text) {
                const val = response.text.trim();
                if (val) {
                  setText(val);
                }
              }
            }
          );
        }
      } catch (err) {
        console.error('Ошибка импорта выделенного текста:', err);
      }
    }
  };

  return (
    <form className={styles.parserForm} onSubmit={handleSubmit}>
      <div className={styles.inputGroup}>
        <div className={styles.textareaHeader}>
          <label className={styles.label}>Текст брифа / задачи:</label>
          {typeof chrome !== 'undefined' && chrome.tabs && (
            <button
              type="button"
              className={styles.btnTextAction}
              onClick={handleImportText}
              title="Импортировать выделенный на текущей вкладке текст"
            >
              ✨ Вставить выделенное
            </button>
          )}
        </div>
        <textarea
          className={styles.textarea}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Вставьте сюда текст брифа или требования к проекту (минимум 10 символов)..."
          rows={10}
          disabled={isLoading}
        />
      </div>

      <button
        type="submit"
        className={`btn btn-primary ${styles.btnSubmit}`}
        disabled={isLoading || text.trim().length < 10}
      >
        {isLoading ? (
          <div className={styles.loaderBtnContainer}>
            <div className={styles.btnSpinner}></div>
            <span>Анализируем...</span>
          </div>
        ) : (
          'Запустить разбор'
        )}
      </button>
    </form>
  );
}
