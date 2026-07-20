import { useState } from 'react';
import styles from './BriefCard.module.css';
import type { BriefAnalysis } from '../../api/types';

interface BriefCardProps {
  analysis: BriefAnalysis;
}

const formatAnalysisAsMarkdown = (analysis: BriefAnalysis): string => {
  const parts: string[] = [];
  parts.push(`# Результат анализа брифа\n\n**Резюме:** ${analysis.summary}\n`);

  if (analysis.recommended_next_action) {
    parts.push(`## 🚀 Рекомендуемый следующий шаг\n${analysis.recommended_next_action}\n`);
  }

  if (analysis.goals && analysis.goals.length > 0) {
    parts.push(`## 🎯 Цели проекта\n${analysis.goals.map((g) => `- ${g}`).join('\n')}\n`);
  }

  if (analysis.deliverables && analysis.deliverables.length > 0) {
    parts.push(`## 📦 Ожидаемые артефакты (Deliverables)\n${analysis.deliverables.map((d) => `- ${d}`).join('\n')}\n`);
  }

  if (analysis.constraints && analysis.constraints.length > 0) {
    parts.push(`## ⏳ Ограничения (Constraints)\n${analysis.constraints.map((c) => `- ${c}`).join('\n')}\n`);
  }

  if (analysis.clarifying_questions && analysis.clarifying_questions.length > 0) {
    parts.push(`## ❓ Уточняющие вопросы к клиенту\n${analysis.clarifying_questions.map((q) => `- ${q}`).join('\n')}\n`);
  }

  if (analysis.risks && analysis.risks.length > 0) {
    parts.push(`## ⚠️ Выявленные риски\n`);
    analysis.risks.forEach((r) => {
      parts.push(`### [${r.severity.toUpperCase()}] ${r.risk}\n- **Причина:** ${r.reason}\n`);
    });
  }

  return parts.join('\n');
};

export function BriefCard({ analysis }: BriefCardProps) {
  const [copiedJson, setCopiedJson] = useState(false);
  const [copiedMd, setCopiedMd] = useState(false);

  const handleCopyJson = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(analysis, null, 2));
      setCopiedJson(true);
      setTimeout(() => setCopiedJson(false), 2000);
    } catch (err) {
      console.error('Не удалось скопировать JSON: ', err);
    }
  };

  const handleCopyMd = async () => {
    try {
      const mdText = formatAnalysisAsMarkdown(analysis);
      await navigator.clipboard.writeText(mdText);
      setCopiedMd(true);
      setTimeout(() => setCopiedMd(false), 2000);
    } catch (err) {
      console.error('Не удалось скопировать Markdown: ', err);
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
        <div className={styles.statusBadge}>✓ Анализ завершен</div>
        <h2 className={styles.cardTitle}>{analysis.summary}</h2>
      </div>

      {analysis.recommended_next_action && (
        <div className={styles.actionBox}>
          <div className={styles.actionHeader}>
            <span>🚀</span> Рекомендуемый следующий шаг
          </div>
          <p className={styles.actionText}>{analysis.recommended_next_action}</p>
        </div>
      )}

      {analysis.goals && analysis.goals.length > 0 && (
        <div className={styles.cardSection}>
          <span className={styles.labelSection}>🎯 Цели проекта:</span>
          <ul className={styles.listContainer}>
            {analysis.goals.map((goal, idx) => (
              <li key={idx} className={styles.listItem}>
                <span className={styles.bullet}>•</span> {goal}
              </li>
            ))}
          </ul>
        </div>
      )}

      {analysis.deliverables && analysis.deliverables.length > 0 && (
        <div className={styles.cardSection}>
          <span className={styles.labelSection}>📦 Ожидаемые артефакты (Deliverables):</span>
          <div className={styles.badgesContainer}>
            {analysis.deliverables.map((item, idx) => (
              <span key={idx} className={styles.badge}>
                {item}
              </span>
            ))}
          </div>
        </div>
      )}

      {analysis.constraints && analysis.constraints.length > 0 && (
        <div className={styles.cardSection}>
          <span className={`${styles.labelSection} ${styles.labelConstraint}`}>
            ⏳ Ограничения (Constraints):
          </span>
          <ul className={styles.listContainer}>
            {analysis.constraints.map((item, idx) => (
              <li key={idx} className={styles.listItem}>
                <span className={styles.bulletWarning}>•</span> {item}
              </li>
            ))}
          </ul>
        </div>
      )}

      {analysis.clarifying_questions && analysis.clarifying_questions.length > 0 && (
        <div className={styles.cardSection}>
          <span className={styles.labelSection}>❓ Уточняющие вопросы к клиенту:</span>
          <ul className={styles.listContainer}>
            {analysis.clarifying_questions.map((question, idx) => (
              <li key={idx} className={styles.listItemQuestion}>
                {question}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className={styles.cardSection}>
        <span className={`${styles.labelSection} ${styles.labelWarning}`}>⚠️ Выявленные риски:</span>
        {analysis.risks && analysis.risks.length > 0 ? (
          <div className={styles.risksContainer}>
            {analysis.risks.map((risk, idx) => (
              <div key={idx} className={styles.riskCard}>
                <div className={styles.riskCardHeader}>
                  <span className={`${styles.riskSeverityBadge} ${getSeverityClass(risk.severity)}`}>
                    {risk.severity.toUpperCase()}
                  </span>
                  <span className={styles.riskDesc}>{risk.risk}</span>
                </div>
                {risk.reason && (
                  <div className={styles.riskReason}>
                    <strong>Причина:</strong> {risk.reason}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className={`${styles.noItemsText} ${styles.textGreen}`}>Риски не обнаружены.</p>
        )}
      </div>

      <div className={styles.buttonsContainer}>
        <button className={`btn btn-secondary ${styles.btnCopy}`} onClick={handleCopyMd}>
          {copiedMd ? '✓ Markdown скопирован!' : '📝 Скопировать в Markdown'}
        </button>
        <button className={`btn btn-secondary ${styles.btnCopy}`} onClick={handleCopyJson}>
          {copiedJson ? '✓ JSON скопирован!' : '📋 Скопировать JSON'}
        </button>
      </div>
    </div>
  );
}
