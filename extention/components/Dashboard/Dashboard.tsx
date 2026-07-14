import { useState, useEffect, useRef } from 'react';
import styles from './Dashboard.module.css';
import { ParserForm } from '../ParserForm/ParserForm';
import { BriefCard } from '../BriefCard/BriefCard';
import { SettingsForm } from '../SettingsForm/SettingsForm';
import { apiService, updateClientConfig } from '../../api/client';
import { DEFAULT_API_URL, STORAGE_KEYS } from '../../config';
import type { BriefResponse } from '../../api/types';

export function Dashboard() {
  const [activeTab, setActiveTab] = useState<'analyzer' | 'settings'>('analyzer');
  const [apiUrl, setApiUrl] = useState(DEFAULT_API_URL);
  const [saveStatus, setSaveStatus] = useState('');
  
  // State for parsing tasks
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState('');
  const [currentBrief, setCurrentBrief] = useState<BriefResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const pollIntervalRef = useRef<number | null>(null);

  // Load initial settings
  useEffect(() => {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.get([STORAGE_KEYS.API_URL], (res) => {
        if (res[STORAGE_KEYS.API_URL]) {
          setApiUrl(res[STORAGE_KEYS.API_URL] as string);
          updateClientConfig(res[STORAGE_KEYS.API_URL] as string);
        }
      });
    }
  }, []);

  // Cleanup polling interval on unmount
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  const handleSaveSettings = () => {
    let cleanUrl = apiUrl.trim();
    if (!cleanUrl) {
      cleanUrl = DEFAULT_API_URL;
      setApiUrl(cleanUrl);
    }

    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.set({ [STORAGE_KEYS.API_URL]: cleanUrl }, () => {
        updateClientConfig(cleanUrl);
        setSaveStatus('Настройки успешно сохранены!');
        setTimeout(() => setSaveStatus(''), 3000);
      });
    } else {
      updateClientConfig(cleanUrl);
      setSaveStatus('Настройки сохранены локально в сессии!');
      setTimeout(() => setSaveStatus(''), 3000);
    }
  };

  const startPolling = (briefId: string) => {
    // Clear any existing poll
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }

    // Set polling status
    setLoadingStatus('Ожидание начала обработки...');

    pollIntervalRef.current = window.setInterval(async () => {
      try {
        const brief = await apiService.getBrief(briefId);
        setCurrentBrief(brief);

        if (brief.status === 'completed') {
          setIsLoading(false);
          setLoadingStatus('');
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
        } else if (brief.status === 'failed') {
          setIsLoading(false);
          setLoadingStatus('');
          setError(brief.error_message || 'Ошибка во время выполнения анализа брифа на сервере.');
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
        } else if (brief.status === 'processing') {
          setLoadingStatus('Идет декодирование и анализ брифа LLM...');
        } else {
          setLoadingStatus('Задача в очереди на обработку...');
        }
      } catch (err: any) {
        console.error('Ошибка опроса статуса брифа:', err);
        setError('Не удалось подключиться к серверу для получения статуса задачи.');
        setIsLoading(false);
        setLoadingStatus('');
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
      }
    }, 2000);
  };

  const handleSubmitBrief = async (text: string) => {
    setIsLoading(true);
    setError(null);
    setCurrentBrief(null);
    setLoadingStatus('Отправка брифа на сервер...');

    try {
      const response = await apiService.parseBrief(text);
      setCurrentBrief(response);
      
      if (response.status === 'completed') {
        setIsLoading(false);
        setLoadingStatus('');
      } else if (response.status === 'failed') {
        setIsLoading(false);
        setLoadingStatus('');
        setError(response.error_message || 'Ошибка разбора брифа.');
      } else {
        // Run is pending or processing, start polling status
        startPolling(response.id);
      }
    } catch (err: any) {
      console.error('Ошибка отправки брифа:', err);
      let errMsg = 'Не удалось соединиться с сервером. Пожалуйста, проверьте URL бэкенда в настройках и статус его работы.';
      if (err.response && err.response.data && err.response.data.detail) {
        if (Array.isArray(err.response.data.detail)) {
          errMsg = err.response.data.detail.map((d: any) => d.msg).join(', ');
        } else {
          errMsg = err.response.data.detail;
        }
      }
      setError(errMsg);
      setIsLoading(false);
      setLoadingStatus('');
    }
  };

  return (
    <div className={styles.dashboardContainer}>
      <header className={styles.dashboardHeader}>
        <h1 className={styles.logo}>
          AI Brief Decoder <span className={styles.logoBadge}>Lite</span>
        </h1>
      </header>

      <nav className={styles.dashboardNav}>
        <button
          className={`${styles.navTab} ${activeTab === 'analyzer' ? styles.active : ''}`}
          onClick={() => setActiveTab('analyzer')}
        >
          🔍 Анализатор
        </button>
        <button
          className={`${styles.navTab} ${activeTab === 'settings' ? styles.active : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          ⚙ Настройки
        </button>
      </nav>

      <main className={styles.dashboardMain}>
        {activeTab === 'analyzer' && (
          <div className={styles.analyzerTabContent}>
            <ParserForm onSubmit={handleSubmitBrief} isLoading={isLoading} />

            {isLoading && loadingStatus && (
              <div className={styles.pollingStatusContainer}>
                <div className={styles.pulseLoader}></div>
                <span className={styles.pollingText}>{loadingStatus}</span>
              </div>
            )}

            {error && (
              <div className={`alert alert-error ${styles.fontSm}`}>
                <strong>Ошибка:</strong> {error}
              </div>
            )}

            {!isLoading && currentBrief?.status === 'completed' && currentBrief.structured_result && (
              <BriefCard analysis={currentBrief.structured_result} />
            )}
          </div>
        )}

        {activeTab === 'settings' && (
          <SettingsForm
            apiUrl={apiUrl}
            setApiUrl={setApiUrl}
            onSave={handleSaveSettings}
            saveStatus={saveStatus}
          />
        )}
      </main>

      <footer className={styles.dashboardFooter}>
        <span>AnytoolAI Prototype v0.1.0</span>
      </footer>
    </div>
  );
}
