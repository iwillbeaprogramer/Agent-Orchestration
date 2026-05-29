function TabNavigation({ tabs, activeTab, onSelectTab }) {
  return (
    <nav className="tabBar" aria-label="Primary tabs">
      {tabs.map((tab) => (
        <button
          className={`tabButton ${activeTab === tab.id ? 'active' : ''}`}
          key={tab.id}
          type="button"
          onClick={() => onSelectTab(tab.id)}
        >
          <span>{tab.label}</span>
        </button>
      ))}
    </nav>
  );
}

export default TabNavigation;
