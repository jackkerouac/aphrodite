'use client';

import React, { useEffect } from 'react';
import { useAboutData } from '@/components/about/hooks';
import { SystemDetailsCard, LinksCard, AcknowledgmentsCard } from '@/components/about';

export default function AboutPage() {
  const { loading, checkingUpdates, data, loadAboutData, checkForUpdates } = useAboutData();

  // Load data on component mount
  useEffect(() => {
    loadAboutData();
  }, []);

  return (
    <div className="about-page max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">About Aphrodite</h1>
      
      {/* System Details Section */}
      <SystemDetailsCard
        systemInfo={data.systemInfo}
        updateInfo={data.updateInfo}
        checkingUpdates={checkingUpdates}
        loading={loading}
        onCheckUpdates={checkForUpdates}
      />
      
      {/* Links Section */}
      <div className="mb-6">
        <LinksCard />
      </div>
      
      {/* Acknowledgments Section */}
      <AcknowledgmentsCard />
    </div>
  );
}
