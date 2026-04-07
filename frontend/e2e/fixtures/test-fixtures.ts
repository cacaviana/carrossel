import { test as base } from '@playwright/test';
import { HomePage } from '../pages/HomePage';
import { CarrosselPage } from '../pages/CarrosselPage';
import { EditorPage } from '../pages/EditorPage';
import { PipelinePage } from '../pages/PipelinePage';
import { AgentesPage } from '../pages/AgentesPage';
import { ConfigPage } from '../pages/ConfigPage';
import { HistoricoPage } from '../pages/HistoricoPage';

type Fixtures = {
  homePage: HomePage;
  carrosselPage: CarrosselPage;
  editorPage: EditorPage;
  pipelinePage: PipelinePage;
  agentesPage: AgentesPage;
  configPage: ConfigPage;
  historicoPage: HistoricoPage;
};

export const test = base.extend<Fixtures>({
  homePage: async ({ page }, use) => {
    await use(new HomePage(page));
  },
  carrosselPage: async ({ page }, use) => {
    await use(new CarrosselPage(page));
  },
  editorPage: async ({ page }, use) => {
    await use(new EditorPage(page));
  },
  pipelinePage: async ({ page }, use) => {
    await use(new PipelinePage(page));
  },
  agentesPage: async ({ page }, use) => {
    await use(new AgentesPage(page));
  },
  configPage: async ({ page }, use) => {
    await use(new ConfigPage(page));
  },
  historicoPage: async ({ page }, use) => {
    await use(new HistoricoPage(page));
  },
});

export { expect } from '@playwright/test';
