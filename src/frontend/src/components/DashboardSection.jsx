import MarketItemCard from './MarketItemCard.jsx';

function DashboardSection({ section, isLoading = false }) {
  if (isLoading) {
    return (
      <article className="sectionPanel">
        <div className="sectionTitleSkeleton skeleton" />
        <div className="itemList">
          {Array.from({ length: 4 }).map((_, index) => (
            <div className="marketCard skeletonCard" key={index} />
          ))}
        </div>
      </article>
    );
  }

  return (
    <article className="sectionPanel">
      <div className="sectionHeader">
        <h2>{section.title}</h2>
        <span>{section.items.length} items</span>
      </div>
      <div className="itemList">
        {section.items.map((item) => (
          <MarketItemCard item={item} key={item.symbol} />
        ))}
      </div>
    </article>
  );
}

export default DashboardSection;
