import styles from './SettingsForm.module.css';
import { DEFAULT_API_URL } from '../../config';

interface SettingsFormProps {
  apiUrl: string;
  setApiUrl: (url: string) => void;
  onSave: () => void;
  saveStatus: string;
}

export function SettingsForm({
  apiUrl,
  setApiUrl,
  onSave,
  saveStatus,
}: SettingsFormProps) {
  return (
    <div className={styles.settingsForm}>
      <div className={styles.inputGroup}>
        <label className={styles.label}>URL Бэкенда:</label>
        <input
          type="text"
          className={styles.input}
          value={apiUrl}
          onChange={(e) => setApiUrl(e.target.value)}
          placeholder={DEFAULT_API_URL}
        />
      </div>

      <button className="btn btn-primary" onClick={onSave}>
        Сохранить настройки
      </button>

      {saveStatus && <div className={styles.saveStatusToast}>{saveStatus}</div>}
    </div>
  );
}
