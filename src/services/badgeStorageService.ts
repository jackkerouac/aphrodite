export const saveBadgeImage = async (
  userId: string,
  type: 'audio' | 'resolution' | 'review',
  imageData: string
): Promise<void> => {
  // Save transparent badge images
  localStorage.setItem(`badge-${userId}-${type}`, imageData);
};

export const getBadgeImage = async (
  userId: string,
  type: 'audio' | 'resolution' | 'review'
): Promise<string | null> => {
  // Create endpoints for retrieving saved badges
  return localStorage.getItem(`badge-${userId}-${type}`);
};

export const associateBadgeWithUser = async (
  userId: string,
  type: 'audio' | 'resolution' | 'review',
  badgeId: string
): Promise<void> => {
  // Add functions for associating badges with users
  localStorage.setItem(`badgeId-${userId}-${type}`, badgeId);
};

export const getBadgeIdForUser = async (
    userId: string,
    type: 'audio' | 'resolution' | 'review'
  ): Promise<string | null> => {
    // Add functions for associating badges with users
    return localStorage.getItem(`badgeId-${userId}-${type}`);
  };