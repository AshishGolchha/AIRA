import React from 'react';
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../context/ThemeContext';
import { ThemeToggle } from '../components/ui/ThemeToggle';

const ThemeInspector: React.FC = () => {
  const { theme } = useTheme();
  return <div data-testid="current-theme">{theme}</div>;
};

describe('Theme Context and ThemeToggle Component', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.className = '';
    document.documentElement.removeAttribute('data-theme');
  });

  it('defaults to light mode when no localStorage preference is saved', () => {
    render(
      <ThemeProvider>
        <ThemeInspector />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-theme').textContent).toBe('light');
    expect(document.documentElement.classList.contains('light')).toBe(true);
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
  });

  it('toggles from light to dark and back when ThemeToggle is clicked', () => {
    render(
      <ThemeProvider>
        <ThemeToggle />
        <ThemeInspector />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-theme').textContent).toBe('light');

    const toggleButton = screen.getByRole('button', { name: /switch to dark mode/i });
    fireEvent.click(toggleButton);

    expect(screen.getByTestId('current-theme').textContent).toBe('dark');
    expect(localStorage.getItem('aira_theme')).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');

    // Click again to return to light mode
    const darkToggleButton = screen.getByRole('button', { name: /switch to light mode/i });
    fireEvent.click(darkToggleButton);

    expect(screen.getByTestId('current-theme').textContent).toBe('light');
    expect(localStorage.getItem('aira_theme')).toBe('light');
    expect(document.documentElement.classList.contains('light')).toBe(true);
  });

  it('renders pill variant with descriptive theme text', () => {
    render(
      <ThemeProvider>
        <ThemeToggle variant="pill" />
      </ThemeProvider>
    );

    expect(screen.getByText(/Light/i)).toBeDefined();

    const pillButton = screen.getByRole('button', { name: /switch to dark mode/i });
    fireEvent.click(pillButton);

    expect(screen.getByText(/Dark/i)).toBeDefined();
  });

  it('restores saved dark mode preference from localStorage on init', () => {
    localStorage.setItem('aira_theme', 'dark');

    render(
      <ThemeProvider>
        <ThemeInspector />
      </ThemeProvider>
    );

    expect(screen.getByTestId('current-theme').textContent).toBe('dark');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
  });
});
