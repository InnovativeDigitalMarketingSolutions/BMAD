import React, { FormEvent } from 'react';

export function LoginForm(): JSX.Element {
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    // TODO: handle login logic
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="email" name="email" placeholder="Email" required />
      <input type="password" name="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
  );
}
