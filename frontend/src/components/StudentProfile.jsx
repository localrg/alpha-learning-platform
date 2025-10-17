import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';

const StudentProfile = ({ onProfileCreated }) => {
  const [name, setName] = useState('');
  const [grade, setGrade] = useState('5');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const token = localStorage.getItem('auth_token');
      
      const response = await fetch('/api/student/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: name.trim(),
          grade: parseInt(grade),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to create profile');
      }

      // Call parent callback with student data
      onProfileCreated(data.student);
      
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create Student Profile</CardTitle>
          <CardDescription>
            Tell us about the student to personalize their learning experience
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="name">Student Name *</Label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter student's name"
                required
                disabled={loading}
                maxLength={100}
              />
              <p className="text-sm text-muted-foreground">
                This is the name that will be used throughout the platform
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="grade">Current Grade *</Label>
              <select
                id="grade"
                value={grade}
                onChange={(e) => setGrade(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                required
                disabled={loading}
              >
                <option value="3">3rd Grade</option>
                <option value="4">4th Grade</option>
                <option value="5">5th Grade</option>
                <option value="6">6th Grade</option>
                <option value="7">7th Grade</option>
                <option value="8">8th Grade</option>
              </select>
              <p className="text-sm text-muted-foreground">
                We'll customize the learning path based on their grade level
              </p>
            </div>

            <div className="p-4 bg-primary/10 rounded-lg">
              <h4 className="font-semibold mb-2">What happens next?</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Take a quick assessment to identify knowledge gaps</li>
                <li>• Get a personalized learning path</li>
                <li>• Start mastering math skills at your own pace</li>
              </ul>
            </div>

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Creating Profile...' : 'Create Profile & Continue'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default StudentProfile;

