export interface PublicCategory {
  id: number;
  name: string;
  description: string;
  display_order: number;
}

export interface PublicService {
  id: number;
  name: string;
  slug: string;
  description: string;
  documentation_url: string;
  featured: boolean;
  updated_at: string;
  categories: PublicCategory[];
}

export interface CategoryGroup {
  id: number;
  name: string;
  description: string;
  display_order: number;
  services: PublicService[];
}

const apiBaseUrl = import.meta.env.API_BASE_URL || 'http://localhost:5000/api';

export async function getPublicServices(): Promise<PublicService[]> {
  try {
    const response = await fetch(`${apiBaseUrl}/public/services`);

    if (!response.ok) {
      throw new Error(`Catalog API returned ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.warn('Nao foi possivel carregar o catalogo publico.', error);
    return [];
  }
}

export function groupServicesByCategory(services: PublicService[]): CategoryGroup[] {
  const groups = new Map<number, CategoryGroup>();
  const uncategorized: CategoryGroup = {
    id: 0,
    name: 'Outros Servicos',
    description: '',
    display_order: 9999,
    services: [],
  };

  for (const service of services) {
    if (!service.categories.length) {
      uncategorized.services.push(service);
      continue;
    }

    for (const category of service.categories) {
      if (!groups.has(category.id)) {
        groups.set(category.id, { ...category, services: [] });
      }

      groups.get(category.id)?.services.push(service);
    }
  }

  const groupedServices = [...groups.values()];
  if (uncategorized.services.length) {
    groupedServices.push(uncategorized);
  }

  return groupedServices
    .map((group) => ({
      ...group,
      services: [...group.services].sort(sortServices),
    }))
    .sort((current, next) => {
      if (current.display_order !== next.display_order) {
        return current.display_order - next.display_order;
      }

      return current.name.localeCompare(next.name);
    });
}

export function sortServices(current: PublicService, next: PublicService): number {
  if (current.featured !== next.featured) {
    return current.featured ? -1 : 1;
  }

  return current.name.localeCompare(next.name);
}
