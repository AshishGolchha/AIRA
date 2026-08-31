import { test, expect } from '@playwright/test';

test.describe('AIRA Critical Browser E2E Workflows', () => {
  let aiGenerationCalled = false;

  test.beforeEach(async ({ page }) => {
    aiGenerationCalled = false;

    // Intercept and mock backend API routes
    await page.route('**/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            access_token: 'mock-e2e-jwt-token',
            token_type: 'Bearer',
            user: {
              id: 1,
              email: 'investor@aira.internal',
              profile: {
                display_name: 'E2E Validation User',
                risk_preference: 'moderate',
                investment_horizon: 'medium_term',
              },
            },
          },
        }),
      });
    });

    await page.route('**/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            user: {
              id: 1,
              email: 'investor@aira.internal',
              profile: {
                display_name: 'E2E Validation User',
                risk_preference: 'moderate',
                investment_horizon: 'medium_term',
              },
            },
          },
        }),
      });
    });

    await page.route('**/api/v1/dashboard', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            user: {
              id: 1,
              name: 'E2E Validation User',
              email: 'investor@aira.internal',
              investment_focus: 'AI Tech',
              risk_tolerance: 'moderate',
              investment_horizon: 'long_term',
            },
            portfolio: {
              total_market_value: 125000.0,
              total_cost_basis: 100000.0,
              unrealized_gain_loss: 25000.0,
              unrealized_gain_loss_percent: 25.0,
              holdings_count: 2,
              top_holdings: [
                {
                  id: 1,
                  symbol: 'NVDA',
                  company_name: 'NVIDIA Corporation',
                  quantity: 50,
                  average_cost: 120.0,
                  current_price: 1500.0,
                  current_value: 75000.0,
                  cost_basis: 6000.0,
                  unrealized_gain_loss: 69000.0,
                  unrealized_gain_loss_percent: 1150.0,
                  allocation_percent: 60.0,
                  currency: 'USD',
                  updated_at: new Date().toISOString(),
                },
              ],
            },
            watchlist: {
              total_count: 1,
              high_priority_count: 1,
              normal_priority_count: 0,
              low_priority_count: 0,
              items: [
                {
                  id: 1,
                  symbol: 'AMD',
                  company_name: 'Advanced Micro Devices',
                  priority: 'high',
                  current_price: 165.0,
                  change: 5.5,
                  change_percent: 3.45,
                  notes: 'Growth catalyst',
                  created_at: new Date().toISOString(),
                },
              ],
            },
            alerts: {
              unread_count: 0,
              critical_count: 0,
              warning_count: 0,
              info_count: 0,
              recent: [],
            },
            research: {
              total_reports: 1,
              recent: [],
            },
            notifications: {
              preferences: {
                in_app_enabled: true,
                email_enabled: false,
                webhook_enabled: true,
                minimum_severity: 'info',
                alert_types: ['price_move', 'portfolio_gain_loss'],
              },
              enabled_channels: ['in_app', 'webhook'],
              pending_retry_count: 0,
              failed_delivery_count: 0,
              delivered_count: 0,
            },
            monitoring: {
              system_monitoring_enabled: true,
              user_alerts_enabled: true,
              latest_run: {
                id: 1,
                status: 'completed',
                started_at: new Date().toISOString(),
                completed_at: new Date().toISOString(),
                duration_seconds: 1.2,
              },
            },
            portfolio_intelligence: {
              available: false,
              latest: null,
            },
          },
        }),
      });
    });

    await page.route('**/api/v1/portfolio/snapshot', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            snapshot: {
              total_market_value: 125000.0,
              total_cost_basis: 100000.0,
              total_unrealized_gain_loss: 25000.0,
              total_unrealized_gain_loss_percent: 25.0,
              holdings_count: 1,
              holdings: [
                {
                  id: 1,
                  symbol: 'NVDA',
                  company_name: 'NVIDIA Corporation',
                  quantity: 50,
                  average_cost: 120.0,
                  current_price: 1500.0,
                  current_value: 75000.0,
                  cost_basis: 6000.0,
                  unrealized_gain_loss: 69000.0,
                  unrealized_gain_loss_percent: 1150.0,
                  allocation_percent: 60.0,
                  currency: 'USD',
                  updated_at: new Date().toISOString(),
                },
              ],
            },
          },
        }),
      });
    });

    await page.route('**/api/v1/portfolio/holdings', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            holdings: [
              {
                id: 1,
                symbol: 'NVDA',
                company_name: 'NVIDIA Corporation',
                quantity: 50,
                average_cost: 120.0,
                current_price: 1500.0,
                current_value: 75000.0,
                cost_basis: 6000.0,
                gain_loss: 69000.0,
                gain_loss_percent: 1150.0,
                allocation_percent: 60.0,
                currency: 'USD',
                updated_at: new Date().toISOString(),
              },
            ],
          },
        }),
      });
    });

    await page.route('**/api/v1/watchlist', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            items: [
              {
                id: 1,
                symbol: 'AMD',
                company_name: 'Advanced Micro Devices',
                priority: 'high',
                current_price: 165.0,
                change: 5.5,
                change_percent: 3.45,
                notes: 'Growth catalyst',
                created_at: new Date().toISOString(),
              },
            ],
            count: 1,
          },
        }),
      });
    });

    await page.route('**/api/v1/alerts*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            alerts: [],
            total: 0,
            unread_count: 0,
          },
        }),
      });
    });

    await page.route('**/api/v1/portfolio/intelligence', async (route) => {
      if (route.request().method() === 'POST') {
        aiGenerationCalled = true;
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              intelligence: {
                id: 99,
                user_id: 1,
                query: null,
                summary: 'E2E synthesized portfolio overview with robust semiconductor exposure.',
                portfolio_overview: 'Strong technology weighting across large-cap leaders.',
                portfolio_risks: ['Hardware cycle duration risk.'],
                portfolio_opportunities: ['Data center AI expansion.'],
                watchlist_priorities: ['Monitor AMD for earnings expansion.'],
                recommended_research: ['Evaluate custom silicon threats.'],
                portfolio_summary: {},
                facts: {},
                sources: [],
                created_at: new Date().toISOString(),
              },
            },
          }),
        });
      } else {
        await route.continue();
      }
    });

    await page.route('**/api/v1/portfolio/intelligence/history*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            history: [],
            total: 0,
            page: 1,
            limit: 10,
          },
        }),
      });
    });

    await page.route('**/api/v1/research/history*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            history: [],
            total: 0,
            page: 1,
            limit: 10,
          },
        }),
      });
    });

    await page.route('**/api/v1/notifications/preferences', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            preferences: {
              in_app_enabled: true,
              email_enabled: false,
              webhook_enabled: true,
              minimum_severity: 'info',
              alert_types: ['price_move', 'portfolio_gain_loss'],
            },
          },
        }),
      });
    });

    await page.route('**/api/v1/notifications/endpoints', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            endpoints: [],
          },
        }),
      });
    });

    await page.route('**/api/v1/notifications/deliveries*', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            deliveries: [],
            total: 0,
            page: 1,
            limit: 20,
          },
        }),
      });
    });

    await page.route('**/api/v1/profile', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          data: {
            profile: {
              id: 1,
              user_id: 1,
              display_name: 'E2E Validation User',
              risk_preference: 'moderate',
              investment_horizon: 'medium_term',
            },
          },
        }),
      });
    });
  });

  test('1. Public root navigation renders Landing Page with branding and CTAs', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL('/');
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Your Investment Research');
    await expect(page.getByText('Autonomous Investment Research Agent').first()).toBeVisible();

    // Verify primary CTA links to register
    const getStartedLink = page.getByRole('link', { name: /Get Started/i }).first();
    await expect(getStartedLink).toBeVisible();
    await getStartedLink.click();
    await expect(page).toHaveURL(/.*register/);
  });

  test('1b. Unauthenticated access to /app/dashboard redirects to /login', async ({ page }) => {
    await page.goto('/app/dashboard');
    await expect(page).toHaveURL(/.*login/);
    await expect(page.getByRole('heading', { name: /AIRA Intelligence/i })).toBeVisible();
  });

  test('2. Successful login transitions to Dashboard', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'investor@aira.internal');
    await page.fill('input[type="password"]', 'Password123!');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL(/.*app\/dashboard/);
    await expect(page.locator('text=E2E Validation User').first()).toBeVisible();
    await expect(page.locator('text=$125,000.00').first()).toBeVisible();
  });

  test('3. Full page navigation flow and Logout', async ({ page }) => {
    // Seed authenticated session
    await page.addInitScript(() => {
      localStorage.setItem('aira_auth_token', 'mock-e2e-jwt-token');
      localStorage.setItem(
        'aira_user',
        JSON.stringify({
          id: 1,
          email: 'investor@aira.internal',
          profile: { display_name: 'E2E Validation User' },
        })
      );
    });

    await page.goto('/app/dashboard');
    await expect(page.locator('text=$125,000.00').first()).toBeVisible();

    // Navigate to Portfolio
    await page.click('a[href="/app/portfolio"]');
    await expect(page).toHaveURL(/.*app\/portfolio/);
    await expect(page.locator('h1').first()).toContainText('Portfolio');

    // Navigate to Watchlist
    await page.click('a[href="/app/watchlist"]');
    await expect(page).toHaveURL(/.*app\/watchlist/);
    await expect(page.locator('h1').first()).toContainText('Watchlist');

    // Navigate to Alerts
    await page.click('a[href="/app/alerts"]');
    await expect(page).toHaveURL(/.*app\/alerts/);
    await expect(page.locator('h1').first()).toContainText('Alert');

    // Navigate to Intelligence
    await page.click('a[href="/app/intelligence"]');
    await expect(page).toHaveURL(/.*app\/intelligence/);
    await expect(page.locator('h1').first()).toContainText('Intelligence');

    // Navigate to Research
    await page.click('a[href="/app/research"]');
    await expect(page).toHaveURL(/.*app\/research/);
    await expect(page.locator('h1').first()).toContainText('Research');

    // Navigate to Notifications
    await page.click('a[href="/app/notifications"]');
    await expect(page).toHaveURL(/.*app\/notifications/);
    await expect(page.locator('h1').first()).toContainText('Notification');

    // Navigate to Settings
    await page.click('a[href="/app/settings"]');
    await expect(page).toHaveURL(/.*app\/settings/);
    await expect(page.locator('h1').first()).toContainText('Profile');
  });

  test('4. Dashboard load is strictly read-only (zero automated AI calls)', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('aira_auth_token', 'mock-e2e-jwt-token');
      localStorage.setItem(
        'aira_user',
        JSON.stringify({
          id: 1,
          email: 'investor@aira.internal',
          profile: { display_name: 'E2E Validation User' },
        })
      );
    });

    await page.goto('/app/dashboard');
    await expect(page.locator('text=$125,000.00').first()).toBeVisible();

    // Verify AI synthesis endpoint was never invoked on dashboard load
    expect(aiGenerationCalled).toBe(false);
  });

  test('5. Portfolio Intelligence requires explicit user trigger', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.setItem('aira_auth_token', 'mock-e2e-jwt-token');
      localStorage.setItem(
        'aira_user',
        JSON.stringify({
          id: 1,
          email: 'investor@aira.internal',
          profile: { display_name: 'E2E Validation User' },
        })
      );
    });

    await page.goto('/app/intelligence');
    await expect(page.locator('h1').first()).toContainText('Intelligence');
    expect(aiGenerationCalled).toBe(false);

    // Explicitly click Generate Report
    await page.click('button[type="submit"]:has-text("Generate")');
    await expect(page.getByText('E2E synthesized portfolio overview')).toBeVisible();
    expect(aiGenerationCalled).toBe(true);
  });
});
