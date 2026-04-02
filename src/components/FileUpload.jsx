import { useId } from 'react';
import '../styles/fileUpload.css';

function FileUpload({
  title,
  description,
  buttonLabel,
  helperText,
  acceptedText,
  accept,
  required = false,
  selectedFileName,
  onFileSelect,
}) {
  const inputId = useId();

  return (
    <section className="file-upload">
      <div className="file-upload__badge">Secure Intake</div>

      <div className="file-upload__copy">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>

      <div className="file-upload__dropzone">
        <input
          className="file-upload__input"
          id={inputId}
          type="file"
          accept={accept}
          required={required}
          onChange={(event) => onFileSelect?.(event.target.files?.[0] ?? null)}
        />
        <label className="file-upload__button" htmlFor={inputId}>
          {buttonLabel}
        </label>
        {selectedFileName ? (
          <strong className="file-upload__filename">{selectedFileName}</strong>
        ) : null}
        <p className="file-upload__helper">{helperText}</p>
        <span className="file-upload__accepted">{acceptedText}</span>
      </div>
    </section>
  );
}

export default FileUpload;
