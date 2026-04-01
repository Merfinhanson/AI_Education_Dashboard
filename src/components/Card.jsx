import '../styles/card.css';

function Card({ title, value, trend, caption }) {
  return (
    <article className="card">
      <p className="card__label">{title}</p>
      <div className="card__value-row">
        <h3>{value}</h3>
        <span className="card__trend">{trend}</span>
      </div>
      <p className="card__caption">{caption}</p>
    </article>
  );
}

export default Card;
