import { useState } from 'react';
import styles from './BriefCard.module.css';
import type { BriefAnalysis } from '../../api/types';

interface BriefCardProps {
  analysis: BriefAnalysis;
}

export function BriefCard({ analysis }: BriefCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(analysis, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Не удалось скопировать текст: ', err);
    }
  };

  const getSeverityClass = (severity: string) => {
    if (severity === 'high') return styles.severityHigh;
    if (severity === 'medium') return styles.severityMedium;
    return styles.severityLow;
  };

  return (
    <div className={styles.briefCardContainer}>
      <div className={styles.cardHeader}>
        <div className={styles.statusBadge}>Анализ завершен</div>
        <h2 className={styles.cardTitle}>{analysis.project_type}</h2>
      </div>

      <div className={styles.cardGrid}>
        <div className={styles.gridItem}>
          <span className={styles.gridLabel}>Бюджет</span>
          <span className={styles.gridValue}>{analysis.budget_info || 'Не указан'}</span>
        </div>
        <div className={styles.gridItem}>
          <span className={styles.gridLabel}>Срок</span>
          <span className={styles.gridValue}>{analysis.deadline_info || 'Не указан'}</span>
        </div>
      </div>

      <div className={styles.cardSection}>
        <span className={styles.labelSection}>Ключевые требования:</span>
        {analysis.key_requirements && analysis.key_requirements.length > 0 ? (
          <div className={styles.badgesContainer}>
            {analysis.key_requirements.map((req, idx) => (
              <span key={idx} className={styles.badge}>
                {req}
              </span>
            ))}
          </div>
        ) : (
          <p className={styles.noItemsText}>Требования не определены.</p>
        )}
      </div>

      <div className={styles.cardSection}>
        <span className={`${styles.labelSection} ${styles.labelWarning}`}>Выявленные риски:</span>
        {analysis.risks && analysis.risks.length > 0 ? (
          <div className={styles.risksContainer}>
            {analysis.risks.map((risk, idx) => (
              <div key={idx} className={styles.riskCard}>
                <div className={styles.riskCardHeader}>
                  <span className={`${styles.riskSeverityBadge} ${getSeverityClass(risk.severity)}`}>
                    {risk.severity.toUpperCase()}
                  </span>
                  <span className={styles.riskDesc}>{risk.description}</span>
                </div>
                {risk.mitigation && (
                  <div className={styles.riskMitigation}>
                    <strong>Рекомендация:</strong> {risk.mitigation}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className={`${styles.noItemsText} ${styles.textGreen}`}>Риски не обнаружены.</p>
        )}
      </div>

      <button className={`btn btn-secondary ${styles.btnCopy}`} onClick={handleCopy}>
        {copied ? '✓ Скопировано!' : '📋 Скопировать JSON-результат'}
      </button>
    </div>
  );
}
